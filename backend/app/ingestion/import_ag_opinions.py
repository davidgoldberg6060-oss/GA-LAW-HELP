"""Discover-only inventory of the Georgia Attorney General opinion index.

Official index: https://law.georgia.gov/opinions (paginated), plus the
official, unofficial, and obsolete-and-modified category indexes. robots.txt
allows ``/opinions``. This module hashes index pages and lists citation labels
and PDF URLs named on those pages. It does not download PDFs, does not invent
opinion text, and does not write corpus rows. ``--discover-only`` and
``--discover-categories`` cannot be combined with ``--commit``. ``--commit`` is
refused while DATABASE_URL is unset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

INDEX = "https://law.georgia.gov/opinions"
HOST = "law.georgia.gov"
USER_AGENT = "GA.LAW.HELP-corpus-import/1.0 (+https://github.com/davidgoldberg6060-oss/GA-LAW-HELP)"
LABEL = re.compile(r"^U?\d{2,4}-\d+$", re.I)
MAX_PAGES = 11  # page=0 through page=10; later pages are short tails
CATEGORY_INDEXES = (
    ("official", "https://law.georgia.gov/opinions/official", 7),
    ("unofficial", "https://law.georgia.gov/opinions/unofficial", 5),
    ("obsolete-and-modified", "https://law.georgia.gov/opinions/obsolete-and-modified-opinions", 1),
)


class _Index(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[dict] = []
        self._href: str | None = None
        self._label: list[str] = []
        self._pdf: str | None = None
        self._pending: dict | None = None
        self._in_row = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self._in_row = True
            self._href = None
            self._label = []
            self._pdf = None
            self._pending = None
        elif tag == "a" and self._in_row:
            href = attrs.get("href") or ""
            if href.startswith("/opinions/") or href.startswith(INDEX):
                self._href = href
                self._label = []
            elif "/document/" in href and href.endswith("/download"):
                self._pdf = href
                self._href = None

    def handle_data(self, data):
        if self._href and self._in_row:
            self._label.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            label = " ".join("".join(self._label).split())
            if LABEL.match(label):
                self._pending = {"label": label, "path": self._href, "pdf_url": self._pdf}
            self._href = None
            self._label = []
        elif tag == "tr" and self._in_row:
            if self._pending:
                self._pending["pdf_url"] = self._pdf
                self.rows.append(self._pending)
            self._in_row = False
            self._pending = None


def parse_index(html: str, *, page_url: str) -> list[dict]:
    parser = _Index()
    parser.feed(html)
    seen: dict[str, dict] = {}
    for row in parser.rows:
        path = row["path"]
        if path.startswith("/"):
            url = urljoin("https://law.georgia.gov", path)
        else:
            url = path
        pdf = row["pdf_url"]
        if pdf and pdf.startswith("/"):
            pdf = urljoin("https://law.georgia.gov", pdf)
        unpublished = bool(pdf and "DO-NOT-SHARE" in pdf)
        item = {
            "citation": row["label"],
            "source_url": url,
            "pdf_url": pdf,
            "gap": (
                "Index names an unpublished PDF URL marked do-not-share; PDF not downloaded."
                if unpublished
                else "Index label only; opinion text not downloaded."
            ),
        }
        seen.setdefault(item["source_url"], item)
    return list(seen.values())


def discover_report(pages: list[dict], *, fetched_at: str) -> dict:
    """pages: {url, sha256, bytes, html} already fetched. Does not open PDFs."""
    opinions: list[dict] = []
    page_rows = []
    for page in pages:
        found = parse_index(page["html"], page_url=page["url"])
        opinions.extend(found)
        page_rows.append({
            "url": page["url"],
            "bytes": page["bytes"],
            "sha256": page["sha256"],
            "labels": len(found),
            "pdf_links": sum(1 for item in found if item["pdf_url"]),
        })
    unique = {item["source_url"]: item for item in opinions}
    unpublished = [item["pdf_url"] for item in unique.values() if item["pdf_url"] and "DO-NOT-SHARE" in item["pdf_url"]]
    return {
        "mode": "discover-only",
        "source": INDEX,
        "fetched_at": fetched_at,
        "committed": False,
        "corpus_rows_written": 0,
        "pages": page_rows,
        "opinion_labels": len(unique),
        "pdf_links_named": sum(1 for item in unique.values() if item["pdf_url"]),
        "unpublished_pdf_urls_not_fetched": unpublished,
        "gap": "Index pages only. Opinion PDFs were not downloaded. Not stored authorities and not current-law verification.",
    }



def discover_categories(pages: list[dict], *, fetched_at: str) -> dict:
    """pages: already fetched category index HTML. Does not open PDFs."""
    report = discover_report(pages, fetched_at=fetched_at)
    report["source"] = "https://law.georgia.gov/opinions/official"
    report["categories"] = sorted({page.get("category") for page in pages if page.get("category")})
    report["gap"] = (
        "Category index pages only. Opinion PDFs were not downloaded. "
        "Not stored authorities and not current-law verification."
    )
    return report


def _fetch(url: str) -> tuple[int, bytes]:
    parsed = urlparse(url)
    allowed = parsed.path.rstrip("/") in {
        "/opinions",
        "/opinions/official",
        "/opinions/unofficial",
        "/opinions/obsolete-and-modified-opinions",
    }
    if parsed.scheme != "https" or parsed.hostname != HOST or not allowed:
        raise ValueError(f"Refusing non-index URL: {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:  # noqa: S310 - host and path allowlisted
        body = response.read()
        if response.status != 200:
            raise ValueError(f"Index returned HTTP {response.status}")
        return response.status, body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover-only", action="store_true", help="Hash index pages and list labels. Do not download PDFs.")
    parser.add_argument("--discover-categories", action="store_true", help="Hash official, unofficial, and obsolete category indexes. Do not download PDFs.")
    parser.add_argument("--commit", action="store_true", help="Refused until DATABASE_URL is set and a reviewed importer exists.")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds between index page requests")
    args = parser.parse_args(argv)
    if args.commit and (args.discover_only or args.discover_categories):
        parser.error("discover modes cannot be combined with --commit")
    if args.discover_only and args.discover_categories:
        parser.error("Pass only one discover mode")
    if args.commit:
        if not os.environ.get("DATABASE_URL"):
            print(json.dumps({"mode": "refused", "reason": "DATABASE_URL is unset; no corpus rows written", "committed": False}))
            return 1
        print(json.dumps({"mode": "refused", "reason": "AG opinion text import is not implemented; no corpus rows written", "committed": False}))
        return 1
    if not args.discover_only and not args.discover_categories:
        parser.error("Pass --discover-only or --discover-categories. This importer does not download opinion text.")
    if not 0.5 <= args.pause <= 30:
        parser.error("pause must be 0.5-30 seconds")
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    pages = []
    targets = []
    if args.discover_categories:
        for category, base, count in CATEGORY_INDEXES:
            for number in range(count):
                url = base if number == 0 else base + "?" + urlencode({"page": number})
                targets.append((category, url))
    else:
        for number in range(MAX_PAGES):
            url = INDEX if number == 0 else INDEX + "?" + urlencode({"page": number})
            targets.append(("", url))
    for index, (category, url) in enumerate(targets):
        _, body = _fetch(url)
        pages.append({
            "category": category,
            "url": url,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "html": body.decode("utf-8", "replace"),
        })
        if index + 1 < len(targets):
            time.sleep(args.pause)
    report = discover_categories(pages, fetched_at=fetched_at) if args.discover_categories else discover_report(pages, fetched_at=fetched_at)
    print(json.dumps(report), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
