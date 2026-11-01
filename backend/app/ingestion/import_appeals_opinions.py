"""Operator-run, resumable import of Court of Appeals of Georgia opinion PDFs.

Same structure as ``import_supreme_opinions``: preview by default, ``--commit`` to persist.
Discovery uses the court's public opinion search (a plain GET form on www.gaappeals.gov,
allowed by robots.txt) for a bounded date window; PDFs are served by efast.gaappeals.gov.

Slip opinions carry no reporter citation, so every record is retained under a clearly marked
``<docket> [UNVERIFIED DOCUMENT ID]`` and keeps unknown currency/precedential status until
later evidence upgrades it. By default only decided direct appeals (``A..A....`` dockets) are
imported; application rulings, dismissals, withdrawals and transfers are skipped unless
``--include-orders`` is given. Consolidated appeals that share one PDF become one record
listing every docket. A docket that links to more than one PDF in the window is
skipped and reported for review instead of guessing which filing is the opinion.
"""
from __future__ import annotations

import argparse
import base64
from pathlib import Path
from dataclasses import dataclass
from datetime import date, timedelta
from html.parser import HTMLParser
import hashlib
import json
import os
import re
import time
from urllib.parse import urlencode, urljoin, urlparse

from .acquisition import FetchResponse
from .http_transport import production_transport
from .security import assert_public_official_url
from .source_acquisition import OfficialDocumentRequest, acquire_ingestion_item
from ..database import SessionLocal
from .pipeline import persist_item

SOURCE_KEY = "ga_appeals_opinion_search"
SEARCH_URL = "https://www.gaappeals.gov/wp-content/themes/benjamin/docket/docketdate/results_all.php"
INDEX_PAGE = "https://www.gaappeals.gov/opinion-search/"
ROBOTS_URL = "https://www.gaappeals.gov/robots.txt"
INDEX_HOSTS = {"www.gaappeals.gov", "gaappeals.gov"}
PDF_HOSTS = {"efast.gaappeals.gov"}
DOCKET = re.compile(r"^A\d{2}[A-Z]\d{4}$")
DIRECT_APPEAL = re.compile(r"^A\d{2}A\d{4}$")
NON_OPINION_RULINGS = ("DISMISSED", "WITHDRAWN", "TRANSFERRED")
INDEX_LIMIT = 3 * 1024 * 1024
MAX_WINDOW_DAYS = 31


@dataclass(frozen=True)
class AppealsOpinion:
    docket: str
    style: str
    judgment_date: str
    ruling: str
    url: str

    @property
    def title(self) -> str:
        return f"{self.docket}. {self.style} ({self.ruling}, {self.judgment_date})"

    @property
    def is_decided_direct_appeal(self) -> bool:
        ruling = self.ruling.upper()
        return bool(DIRECT_APPEAL.match(self.docket)) and not any(word in ruling for word in NON_OPINION_RULINGS)


class _ResultsTable(HTMLParser):
    """Collect <tr> rows: cell texts plus the official PDF link."""

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.rows: list[tuple[list[str], str | None]] = []
        self._cells: list[str] | None = None
        self._cell: list[str] | None = None
        self._pdf: str | None = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self._cells, self._pdf = [], None
        elif tag == "td" and self._cells is not None:
            self._cell = []
        elif tag == "a" and self._cells is not None and "link-pdf" in (attrs.get("class") or "").split():
            href = attrs.get("href")
            if href:
                self._pdf = urljoin(self.base_url, href)

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self._cells is not None and self._cell is not None:
            self._cells.append(" ".join(" ".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._cells is not None:
            self.rows.append((self._cells, self._pdf))
            self._cells = None


def _official_pdf(url: str | None) -> str | None:
    if not url:
        return None
    try:
        assert_public_official_url(url)
    except ValueError:
        return None
    return url if urlparse(url).hostname in PDF_HOSTS else None



def _checkpoint_page(url: str, response) -> dict:
    """Hash an index or robots response. Never follow a PDF link."""
    body = response.body or b""
    text = body.decode("utf-8", errors="replace")
    captcha = (
        response.status_code != 200
        or "Human Verification" in text
        or "awsWafCookieDomainList" in text
    )
    return {
        "url": url,
        "final_url": response.url,
        "status_code": response.status_code,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "pdf_links_named": 0,
        "waf_captcha": captcha,
        "downloaded_pdfs": 0,
        "gap": (
            "WAF captcha or non-200; not an opinion index; PDFs not named or downloaded"
            if captcha
            else "Index HTML hashed only; opinion PDFs not downloaded"
        ),
    }


def discover_index(transport=production_transport) -> dict:
    """Read the public opinion-search page and robots.txt only.

    Does not call the date-search endpoint and does not download efast PDFs.
    """
    pages = []
    for url in (INDEX_PAGE, ROBOTS_URL):
        response = transport(assert_public_official_url(url))
        pages.append(_checkpoint_page(url, response))
    return {
        "mode": "discover-only",
        "committed": False,
        "pdfs_downloaded": 0,
        "search_endpoint_requested": False,
        "pages": pages,
        "note": "Index checkpoint only. No opinion PDFs downloaded and no corpus rows written.",
    }


def search_url(start: date, end: date) -> str:
    return SEARCH_URL + "?" + urlencode({"OPstartDate": start.isoformat(), "OPendDate": end.isoformat(), "submit": "Start Opinions Search"})


def parse_results(html: str, base_url: str = SEARCH_URL) -> tuple[list[AppealsOpinion], list[str]]:
    """Return (unique opinions, ambiguous dockets). Repeated identical rows are merged."""
    parser = _ResultsTable(base_url)
    parser.feed(html)
    by_docket: dict[str, dict[str, AppealsOpinion]] = {}
    for cells, pdf in parser.rows:
        if len(cells) < 4 or not DOCKET.match(cells[0].upper()):
            continue
        url = _official_pdf(pdf)
        if url is None:
            continue
        item = AppealsOpinion(cells[0].upper(), cells[1], cells[2], cells[3], url)
        by_docket.setdefault(item.docket, {}).setdefault(item.url, item)
    ambiguous = sorted(docket for docket, urls in by_docket.items() if len(urls) > 1)
    unique = [next(iter(urls.values())) for docket, urls in by_docket.items() if len(urls) == 1]
    return unique, ambiguous


def discover_window(start: date, end: date, transport=production_transport) -> tuple[list[AppealsOpinion], list[str]]:
    if end < start:
        raise ValueError("End date precedes start date")
    if (end - start).days >= MAX_WINDOW_DAYS:
        raise ValueError(f"Search window must be at most {MAX_WINDOW_DAYS} days")
    url = search_url(start, end)
    response = transport(assert_public_official_url(url))
    if response.status_code != 200 or len(response.body) > INDEX_LIMIT:
        raise ValueError(f"Unable to read bounded opinion search results for {start}..{end}")
    if urlparse(response.url).hostname not in INDEX_HOSTS:
        raise ValueError("Opinion search redirected outside the court host")
    content_type = next((v for k, v in response.headers.items() if k.lower() == "content-type"), "")
    if not content_type.lower().startswith("text/html"):
        raise ValueError("Opinion search did not return HTML")
    html = response.body.decode("utf-8", errors="replace")
    if "Results for dates" not in html:
        raise ValueError("Unexpected opinion search layout; inspect the results page")
    return parse_results(html, response.url)


def windows(start: date, end: date):
    cursor = start
    while cursor <= end:
        stop = min(end, cursor + timedelta(days=MAX_WINDOW_DAYS - 1))
        yield cursor, stop
        cursor = stop + timedelta(days=1)


def discover(start: date, end: date, *, include_orders: bool = False, transport=production_transport, pause: float = 0.0):
    opinions: list[AppealsOpinion] = []
    ambiguous: list[str] = []
    for window_start, window_end in windows(start, end):
        found, unclear = discover_window(window_start, window_end, transport)
        opinions.extend(found)
        ambiguous.extend(unclear)
        if pause:
            time.sleep(pause)
    seen: dict[str, AppealsOpinion] = {}
    for item in opinions:
        if item.docket in seen and seen[item.docket].url != item.url:
            ambiguous.append(item.docket)
        seen.setdefault(item.docket, item)
    ambiguous_set = set(ambiguous)
    result = [o for o in seen.values() if o.docket not in ambiguous_set]
    if not include_orders:
        result = [o for o in result if o.is_decided_direct_appeal]
    return _merge_consolidated(result), sorted(ambiguous_set)


def _merge_consolidated(opinions: list[AppealsOpinion]) -> list[AppealsOpinion]:
    """Consolidated appeals share one opinion PDF: keep one record listing every docket."""
    by_url: dict[str, list[AppealsOpinion]] = {}
    for item in opinions:
        by_url.setdefault(item.url, []).append(item)
    merged = []
    for url, items in by_url.items():
        items.sort(key=lambda o: o.docket)
        if len(items) == 1:
            merged.append(items[0])
            continue
        rulings = list(dict.fromkeys(o.ruling for o in items))
        merged.append(AppealsOpinion(", ".join(o.docket for o in items), items[0].style, items[0].judgment_date, "; ".join(rulings), url))
    return merged


def _page_name(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json"


def saving_transport(transport, folder: str):
    """Wrap ``transport`` so each official response is also saved verbatim (base64) under ``folder``.

    Used on an operator machine when the court refuses CI runner IPs; the folder is then
    published as a release and replayed by ``replay_transport`` in the import workflow."""
    Path(folder).mkdir(parents=True, exist_ok=True)

    def run(url: str) -> FetchResponse:
        got = transport(url)
        if got.status_code == 200:
            Path(folder, _page_name(url)).write_text(json.dumps({
                "url": url, "final_url": got.url, "status_code": got.status_code, "headers": dict(got.headers),
                "sha256": hashlib.sha256(got.body).hexdigest(), "body_b64": base64.b64encode(got.body).decode()}))
        return got
    return run


def replay_transport(folder: str):
    """Serve responses saved by ``saving_transport``; verifies each body's sha256 and official URL."""
    def run(url: str) -> FetchResponse:
        assert_public_official_url(url)
        path = Path(folder, _page_name(url))
        if not path.is_file():
            return FetchResponse(url=url, status_code=404, headers={}, body=b"")
        data = json.loads(path.read_text())
        body = base64.b64decode(data["body_b64"])
        if data["url"] != url or hashlib.sha256(body).hexdigest() != data["sha256"]:
            raise ValueError(f"saved page failed integrity check: {url}")
        assert_public_official_url(data["final_url"])
        return FetchResponse(url=data["final_url"], status_code=data["status_code"], headers=data["headers"], body=body)
    return run


def prepare_opinion(opinion: AppealsOpinion, *, transport=production_transport):
    """Acquire one opinion PDF; always retained under the docket-labeled unverified ID."""
    request = OfficialDocumentRequest(
        source_key=SOURCE_KEY,
        url=opinion.url,
        title=opinion.title,
        external_id=opinion.docket,
    )
    item = acquire_ingestion_item(request, transport=transport, allow_unverified_identifier=True)
    return with_pdf_text(item)


def with_pdf_text(item):
    """Store the opinion's extracted text, not raw PDF bytes (which contain NULs Postgres rejects)."""
    import dataclasses
    from .import_ga_regulations import pdf_text
    document = item.document
    if document.extracted_text is not None or not document.body.startswith(b"%PDF"):
        return item
    text = pdf_text(document.body).replace("\x00", "").strip()
    if not text:
        raise ValueError("opinion PDF has no extractable text")
    return dataclasses.replace(item, document=dataclasses.replace(document, extracted_text=text))


def main(argv: list[str] | None = None, *, transport=production_transport, session_factory=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, help="First judgment date (YYYY-MM-DD)")
    parser.add_argument("--end", type=date.fromisoformat, help="Last judgment date (YYYY-MM-DD)")
    parser.add_argument("--discover-only", action="store_true", help="Hash the opinion-search page and robots.txt only; do not download opinions or open a database")
    parser.add_argument("--limit", type=int, default=100, help="Maximum PDFs per run (1-500)")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many discovered opinions for a later batch")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds between court requests")
    parser.add_argument("--include-orders", action="store_true", help="Also import application rulings, dismissals, withdrawals and transfers")
    parser.add_argument("--commit", action="store_true", help="Persist each acquired document")
    parser.add_argument("--save-pages", help="Also save every fetched official response to this folder (for runner-blocked sites)")
    parser.add_argument("--pages-dir", help="Replay official responses saved by --save-pages instead of the network")
    args = parser.parse_args(argv)
    if args.save_pages and args.pages_dir:
        parser.error("--save-pages and --pages-dir cannot be combined")
    if args.pages_dir:
        transport = replay_transport(args.pages_dir)
    elif args.save_pages:
        transport = saving_transport(transport, args.save_pages)
    if args.commit and args.discover_only:
        parser.error("--commit cannot be combined with --discover-only")
    if args.discover_only:
        print(json.dumps(discover_index(transport)), flush=True)
        return 0
    if args.start is None or args.end is None:
        parser.error("--start and --end are required unless --discover-only is set")
    if args.commit and not os.environ.get("DATABASE_URL"):
        parser.error("DATABASE_URL is unset; refusing to write corpus rows")
    if not 1 <= args.limit <= 500 or args.offset < 0 or not 0.5 <= args.pause <= 30:
        parser.error("Limit must be 1-500, offset nonnegative, and pause 0.5-30 seconds")
    if args.end < args.start or (args.end - args.start).days > 366:
        parser.error("Choose an end date on/after the start date, at most one year later")
    opinions, ambiguous = discover(args.start, args.end, include_orders=args.include_orders, transport=transport, pause=args.pause)
    for docket in ambiguous:
        print(json.dumps({"mode": "skipped", "docket": docket, "reason": "multiple PDFs for one docket; review manually"}), flush=True)
    session_factory = session_factory or SessionLocal
    success = errors = 0
    batch = opinions[args.offset:args.offset + args.limit]
    for opinion in batch:
        try:
            item = prepare_opinion(opinion, transport=transport)
            authority_id = None
            if args.commit:
                with session_factory() as db:
                    try:
                        saved = persist_item(db, item)
                        db.commit()
                        authority_id = saved.id
                    except Exception:
                        db.rollback()
                        raise
            success += 1
            print(json.dumps({"mode": "committed" if args.commit else "preview", "docket": opinion.docket,
                              "citation": item.citation, "ruling": opinion.ruling, "judgment_date": opinion.judgment_date,
                              "unverified_identifier": True, "authority_id": authority_id, "source_url": opinion.url}), flush=True)
        except Exception as exc:
            errors += 1
            print(json.dumps({"mode": "error", "docket": opinion.docket, "error_type": type(exc).__name__}), flush=True)
        time.sleep(args.pause)
    print(json.dumps({"start": args.start.isoformat(), "end": args.end.isoformat(), "discovered": len(opinions),
                      "ambiguous_skipped": len(ambiguous), "offset": args.offset, "attempted": len(batch),
                      "succeeded": success, "failed": errors, "committed": args.commit}), flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
