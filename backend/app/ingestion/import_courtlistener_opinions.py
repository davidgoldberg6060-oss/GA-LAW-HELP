"""Operator-run, resumable import of Georgia appellate opinions from CourtListener.

Source: Free Law Project's CourtListener bulk data (preferred), published quarterly on
``com-courtlistener-storage.s3-us-west-2.amazonaws.com/bulk-data/`` "free of known copyright
restrictions". Courts: ``ga`` (Supreme Court of Georgia) and ``gactapp`` (Court of Appeals of
Georgia). An optional REST API mode (``--source api``) needs ``COURTLISTENER_TOKEN`` and is
meant for small incremental top-ups; bulk files remain the default.

Preview by default; ``--commit`` persists into legal_authorities/authority_versions.

Bulk files are streamed (HTTP -> bz2 -> csv) and never fully loaded into memory or disk:
1. dockets, clusters and citations build a small Georgia index (cached with ``--index-cache``);
2. the opinions file is streamed once and filtered to that index.
``--state-file`` checkpoints (in commit mode only) the opinions row position and imported clusters
so an interrupted run resumes where it stopped; rows before the checkpoint are still decompressed
but not processed (``--offset``/``--limit`` bound a batch of matched records).

CourtListener is a third-party aggregator, so every record stays ``unverified`` with unknown
currency/precedential status. Citation keys reuse the formats of the official importers so the
same case is not stored twice: an explicit ``N Ga. N``/``N Ga. App. N`` reporter citation, else a
modern docket ``<docket> [UNVERIFIED DOCUMENT ID]``, else ``CourtListener cluster <id>
[UNVERIFIED DOCUMENT ID]``. On commit, a case already stored from an official court source is
skipped (official text wins); only the lead/majority opinion of each cluster is stored.
"""
from __future__ import annotations

import argparse
import bz2
import csv
import io
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Iterable, Iterator
from urllib.parse import urlencode, urlparse
import urllib.request

from .models import LegalStatus, SourceDocument
from .persistence import upsert_authority_document

SOURCE_KEY = "courtlistener_bulk"
BULK_BASE = "https://com-courtlistener-storage.s3-us-west-2.amazonaws.com/bulk-data/"
API_BASE = "https://www.courtlistener.com/api/rest/v4/"
WEB_BASE = "https://www.courtlistener.com"
ALLOWED_HOSTS = {"com-courtlistener-storage.s3-us-west-2.amazonaws.com", "www.courtlistener.com"}
USER_AGENT = "GA.LAW.HELP-corpus-import/1.0 (+https://github.com/davidgoldberg6060-oss/GA-LAW-HELP)"
COURTS = {"ga": "Ga.", "gactapp": "Ga. App."}  # court id -> official reporter abbreviation
# Lead/majority opinion types; concurrences, dissents, remittiturs etc. are not stored separately.
MAIN_TYPES = ("010combined", "015unamimous", "020lead", "025plurality", "080onthemerits")
TEXT_FIELDS = ("html_with_citations", "plain_text", "html", "html_lawbox", "html_columbia",
               "html_anon_2020", "xml_harvard")
MODERN_DOCKET = re.compile(r"^[SA]\d{2}[A-Z]\d{4}$")
BULK_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
csv.field_size_limit((1 << 31) - 1)


# ---------------------------------------------------------------- streaming helpers
def check_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Refusing non-CourtListener URL: {url}")
    return url


def _open(location: str):
    if location.startswith(("http://", "https://")):
        request = urllib.request.Request(check_url(location), headers={"User-Agent": USER_AGENT})
        raw = urllib.request.urlopen(request, timeout=120)  # noqa: S310 - host allowlisted above
    else:
        raw = open(location, "rb")
    return bz2.BZ2File(raw) if location.endswith(".bz2") else raw


def csv_rows(location: str) -> Iterator[dict]:
    """Stream rows of a CourtListener bulk CSV (Postgres COPY, backslash escapes)."""
    with _open(location) as binary:
        text = io.TextIOWrapper(binary, encoding="utf-8", newline="")
        yield from csv.DictReader(text, escapechar="\\")


def bulk_url(kind: str, bulk_date: str) -> str:
    if not BULK_DATE.match(bulk_date):
        raise ValueError("bulk date must be YYYY-MM-DD")
    return f"{BULK_BASE}{kind}-{bulk_date}.csv.bz2"


def latest_bulk_date(fetch_text: Callable[[str], str] | None = None) -> str:
    """Newest date for which opinions, clusters, dockets and citations files all exist."""
    fetch_text = fetch_text or _fetch_text
    listing_base = "https://com-courtlistener-storage.s3-us-west-2.amazonaws.com/"
    dates: dict[str, set[str]] = {}
    for kind in ("opinions", "opinion-clusters", "dockets", "citations"):
        xml = fetch_text(listing_base + "?" + urlencode({"list-type": "2", "prefix": f"bulk-data/{kind}-"}))
        found = re.findall(rf"<Key>bulk-data/{re.escape(kind)}-(\d{{4}}-\d{{2}}-\d{{2}})\.csv\.bz2</Key>", xml)
        dates[kind] = set(found)
    common = set.intersection(*dates.values())
    if not common:
        raise ValueError("No complete CourtListener bulk snapshot found")
    return max(common)


def _fetch_text(url: str, headers: dict | None = None) -> str:
    request = urllib.request.Request(check_url(url), headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        return response.read().decode("utf-8")


class _Text(HTMLParser):
    BLOCK = {"p", "div", "br", "h1", "h2", "h3", "h4", "li", "tr", "blockquote", "pre", "opinion"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def opinion_text(row: dict) -> str:
    for name in TEXT_FIELDS:
        value = (row.get(name) or "").strip()
        if not value:
            continue
        if name != "plain_text":
            parser = _Text()
            parser.feed(value)
            value = "".join(parser.parts)
        value = re.sub(r"[ \t\r\f\v]+", " ", value)
        value = re.sub(r"\n\s*\n\s*", "\n\n", value).strip()
        if value:
            return value
    return ""


# ---------------------------------------------------------------- records
@dataclass
class ClusterMeta:
    cluster_id: str
    court: str
    docket_number: str
    case_name: str
    date_filed: str
    slug: str
    cl_precedential_status: str
    citations: list[str] = field(default_factory=list)

    @property
    def citation(self) -> str:
        reporter = sorted(set(self.citations))
        if len(reporter) == 1:
            return reporter[0]
        return self.docket_key or f"CourtListener cluster {self.cluster_id} [UNVERIFIED DOCUMENT ID]"

    @property
    def docket_key(self) -> str | None:
        docket = re.sub(r"\s+", "", self.docket_number or "").upper()
        return f"{docket} [UNVERIFIED DOCUMENT ID]" if MODERN_DOCKET.match(docket) else None

    @property
    def dedupe_keys(self) -> list[str]:
        keys = sorted(set(self.citations)) + [self.docket_key or ""] + [self.citation]
        return list(dict.fromkeys(k for k in keys if k))

    @property
    def url(self) -> str:
        return f"{WEB_BASE}/opinion/{int(self.cluster_id)}/{self.slug or 'opinion'}/"


@dataclass
class OpinionRecord:
    meta: ClusterMeta
    opinion_id: str
    opinion_type: str
    text: str
    snapshot: str  # "bulk-YYYY-MM-DD" or "api"

    def document(self, retrieved_at: datetime) -> SourceDocument:
        published = None
        if re.match(r"^\d{4}-\d{2}-\d{2}$", self.meta.date_filed or ""):
            published = datetime.fromisoformat(self.meta.date_filed).replace(tzinfo=timezone.utc)
        return SourceDocument(
            source_key=SOURCE_KEY,
            url=self.meta.url,
            title=self.meta.case_name or f"CourtListener cluster {self.meta.cluster_id}",
            body=self.text.encode("utf-8"),
            retrieved_at=retrieved_at,
            published_at=published,
            external_id=f"courtlistener:{self.snapshot}:opinion:{self.opinion_id}",
            content_type="text/plain",
            metadata={"authority_type": "case_law", "jurisdiction": "Georgia",
                      "court": self.meta.court, "docket_number": self.meta.docket_number,
                      "cluster_id": self.meta.cluster_id, "date_filed": self.meta.date_filed,
                      "courtlistener_precedential_status": self.meta.cl_precedential_status},
            legal_status=LegalStatus(),  # third-party aggregator: unverified / unknown
            extracted_text=self.text,
        )

    def preview(self) -> dict:
        return {"cluster_id": self.meta.cluster_id, "opinion_id": self.opinion_id,
                "court": self.meta.court, "citation": self.meta.citation,
                "case_name": self.meta.case_name, "date_filed": self.meta.date_filed,
                "type": self.opinion_type, "chars": len(self.text),
                "sha256": sha256(self.text.encode("utf-8")).hexdigest(), "source_url": self.meta.url}


# ---------------------------------------------------------------- bulk index + stream
def build_index(dockets: str, clusters: str, citations: str, courts: Iterable[str] = COURTS) -> dict[str, ClusterMeta]:
    courts = set(courts)
    docket_info: dict[str, tuple[str, str]] = {}
    for row in csv_rows(dockets):
        if row.get("court_id") in courts:
            docket_info[row["id"]] = (row["court_id"], row.get("docket_number") or "")
    index: dict[str, ClusterMeta] = {}
    for row in csv_rows(clusters):
        info = docket_info.get(row.get("docket_id") or "")
        if info is None:
            continue
        index[row["id"]] = ClusterMeta(
            cluster_id=row["id"], court=info[0], docket_number=info[1],
            case_name=(row.get("case_name") or row.get("case_name_full") or "").strip(),
            date_filed=row.get("date_filed") or "", slug=row.get("slug") or "",
            cl_precedential_status=row.get("precedential_status") or "")
    for row in csv_rows(citations):
        meta = index.get(row.get("cluster_id") or "")
        if meta is None or row.get("reporter") != COURTS[meta.court]:
            continue
        try:
            meta.citations.append(f"{int(row['volume'])} {row['reporter']} {int(row['page'])}")
        except (TypeError, ValueError):
            continue
    return index


def save_index(index: dict[str, ClusterMeta], path: str, bulk_date: str = "") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    payload = {"bulk_date": bulk_date, "clusters": {k: vars(v) for k, v in index.items()}}
    Path(path).write_text(json.dumps(payload), encoding="utf-8")


def load_index(path: str, bulk_date: str = "") -> dict[str, ClusterMeta] | None:
    """Cached index for the same snapshot, or None (missing/other snapshot -> rebuild)."""
    if not Path(path).exists():
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("bulk_date", "") != bulk_date:
        return None
    return {k: ClusterMeta(**v) for k, v in payload["clusters"].items()}


def stream_bulk_opinions(opinions: str, index: dict[str, ClusterMeta], state: dict, snapshot: str) -> Iterator[OpinionRecord | None]:
    """Yield matched records; ``None`` marks a scanned-but-skipped row (lets callers checkpoint)."""
    skip = int(state.get("rows_scanned", 0))
    done = set(state.setdefault("clusters_done", []))
    counts = state.setdefault("counts", {})
    for number, row in enumerate(csv_rows(opinions)):
        if number < skip:
            continue
        state["rows_scanned"] = number + 1
        meta = index.get(row.get("cluster_id") or "")
        if meta is None:
            yield None
            continue
        if row.get("type") not in MAIN_TYPES:
            counts["skipped_separate_opinions"] = counts.get("skipped_separate_opinions", 0) + 1
            yield None
            continue
        if meta.cluster_id in done:
            counts["skipped_second_majority"] = counts.get("skipped_second_majority", 0) + 1
            yield None
            continue
        text = opinion_text(row)
        if not text:
            counts["skipped_no_text"] = counts.get("skipped_no_text", 0) + 1
            yield None
            continue
        done.add(meta.cluster_id)
        state["clusters_done"].append(meta.cluster_id)
        yield OpinionRecord(meta, row.get("id") or "", row.get("type") or "", text, snapshot)


# ---------------------------------------------------------------- API (optional, token)
def stream_api_opinions(token: str, courts: Iterable[str], state: dict, *, pause: float,
                        fetch_json: Callable[[str], dict] | None = None) -> Iterator[OpinionRecord | None]:
    if not token:
        raise ValueError("COURTLISTENER_TOKEN is required for --source api")

    def default_fetch(url: str) -> dict:
        time.sleep(pause)
        return json.loads(_fetch_text(url, {"Authorization": f"Token {token}"}))

    fetch_json = fetch_json or default_fetch
    cursors = state.setdefault("api_next", {})
    done = set(state.setdefault("clusters_done", []))
    for court in courts:
        url = cursors.get(court) or API_BASE + "clusters/?" + urlencode({
            "docket__court": court, "order_by": "id",
            "fields": "id,case_name,date_filed,docket,docket_id,precedential_status,citations,slug"})
        while url:
            page = fetch_json(check_url(url))
            for cluster in page.get("results", []):
                cid = str(cluster["id"])
                if cid in done:
                    yield None
                    continue
                docket_id = cluster.get("docket_id") or str(cluster.get("docket", "")).rstrip("/").rsplit("/", 1)[-1]
                docket = fetch_json(check_url(f"{API_BASE}dockets/{int(docket_id)}/?fields=docket_number,court_id"))
                meta = ClusterMeta(cid, court, docket.get("docket_number") or "", cluster.get("case_name") or "",
                                   cluster.get("date_filed") or "", cluster.get("slug") or "",
                                   cluster.get("precedential_status") or "")
                for cite in cluster.get("citations") or []:
                    if cite.get("reporter") == COURTS[court]:
                        meta.citations.append(f"{int(cite['volume'])} {cite['reporter']} {int(cite['page'])}")
                ops = fetch_json(check_url(API_BASE + "opinions/?" + urlencode(
                    {"cluster": cid, "fields": "id,type," + ",".join(TEXT_FIELDS)})))
                lead = sorted((o for o in ops.get("results", []) if o.get("type") in MAIN_TYPES),
                              key=lambda o: (o.get("type"), o.get("id")))
                text = opinion_text(lead[0]) if lead else ""
                done.add(cid)
                state["clusters_done"].append(cid)
                yield OpinionRecord(meta, str(lead[0]["id"]), lead[0]["type"], text, "api") if text else None
            url = page.get("next")
            cursors[court] = url
        cursors[court] = None


# ---------------------------------------------------------------- persistence
def is_courtlistener_url(url: str | None) -> bool:
    return (urlparse(url or "").hostname or "") in ALLOWED_HOSTS


def persist_record(db, record: OpinionRecord, retrieved_at: datetime) -> tuple[str, int]:
    from ..models import LegalAuthority

    existing = (db.query(LegalAuthority)
                .filter(LegalAuthority.jurisdiction == "Georgia",
                        LegalAuthority.citation.in_(record.meta.dedupe_keys)).all())
    official = [row for row in existing if not is_courtlistener_url(row.source_url)]
    if official:
        return "duplicate_of_official", official[0].id
    saved = upsert_authority_document(db, document=record.document(retrieved_at), jurisdiction="Georgia",
                                      authority_type="case_law", citation=record.meta.citation)
    return "committed", saved.id


# ---------------------------------------------------------------- CLI
def _load_state(path: str | None) -> dict:
    if path and Path(path).exists():
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return {}


def _save_state(path: str | None, state: dict) -> None:
    if path:
        tmp = Path(path).with_suffix(".tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        tmp.replace(path)


def main(argv: list[str] | None = None, *, session_factory=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", choices=("bulk", "api"), default="bulk")
    parser.add_argument("--court", default="ga,gactapp", help="Comma list of: ga, gactapp")
    parser.add_argument("--bulk-date", default="latest", help="Bulk snapshot date YYYY-MM-DD or 'latest'")
    for kind in ("dockets", "clusters", "citations", "opinions"):
        parser.add_argument(f"--{kind}-file", help=f"Local path or CourtListener URL overriding the {kind} file")
    parser.add_argument("--index-cache", help="JSON file caching the Georgia cluster index between runs")
    parser.add_argument("--state-file", help="JSON checkpoint for resuming (rows scanned, clusters done, API cursor)")
    parser.add_argument("--limit", type=int, default=100, help="Max records this run (1-50000)")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many matched records first")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds between API requests (api mode)")
    parser.add_argument("--commit", action="store_true", help="Persist records (default: preview only)")
    parser.add_argument("--quiet", action="store_true", help="Only print the summary line")
    args = parser.parse_args(argv)
    courts = [c.strip() for c in args.court.split(",") if c.strip()]
    if not courts or any(c not in COURTS for c in courts):
        parser.error("--court must be a comma list of ga, gactapp")
    if not 1 <= args.limit <= 50000 or args.offset < 0 or not 0.75 <= args.pause <= 30:
        parser.error("limit must be 1-50000, offset nonnegative, pause 0.75-30 seconds")
    if args.offset and args.state_file:
        parser.error("use either --offset (ad-hoc batches) or --state-file (checkpointed resume), not both")

    state = _load_state(args.state_file)
    started = time.time()
    if args.source == "bulk":
        bulk_date = args.bulk_date
        files = {k: getattr(args, f"{k}_file") for k in ("dockets", "clusters", "citations", "opinions")}
        if all(files.values()) and bulk_date == "latest":
            found = re.search(r"(\d{4}-\d{2}-\d{2})\.csv", files["opinions"])
            bulk_date = found.group(1) if found else "local"
        if not all(files.values()):
            bulk_date = latest_bulk_date() if bulk_date == "latest" else bulk_date
            names = {"dockets": "dockets", "clusters": "opinion-clusters", "citations": "citations", "opinions": "opinions"}
            files = {k: v or bulk_url(names[k], bulk_date) for k, v in files.items()}
        if state.get("bulk_date") not in (None, bulk_date):
            parser.error(f"state file is for bulk snapshot {state['bulk_date']}, not {bulk_date}")
        state["bulk_date"] = bulk_date
        index = load_index(args.index_cache, bulk_date) if args.index_cache else None
        if index is None:
            # The cache always covers both Georgia courts so a later --court run can reuse it.
            index = build_index(files["dockets"], files["clusters"], files["citations"])
            if args.index_cache:
                save_index(index, args.index_cache, bulk_date)
        index = {k: v for k, v in index.items() if v.court in courts}
        records = stream_bulk_opinions(files["opinions"], index, state, f"bulk-{bulk_date}")
        header = {"source": "courtlistener-bulk", "bulk_date": bulk_date, "files": files, "georgia_clusters": len(index)}
    else:
        records = stream_api_opinions(os.environ.get("COURTLISTENER_TOKEN", ""), courts, state, pause=args.pause)
        header = {"source": "courtlistener-api"}
    if not args.quiet:
        print(json.dumps({"mode": "start", **header}), flush=True)

    session_factory = session_factory
    if args.commit and session_factory is None:
        from ..database import SessionLocal
        session_factory = SessionLocal
    retrieved_at = datetime.now(timezone.utc)
    matched = handled = failed = 0
    outcomes: dict[str, int] = {}
    by_court: dict[str, int] = {}
    last_save = time.time()
    for record in records:
        if args.commit and time.time() - last_save > 30:
            _save_state(args.state_file, state)
            last_save = time.time()
        if record is None:
            continue
        matched += 1
        if matched <= args.offset:
            continue
        by_court[record.meta.court] = by_court.get(record.meta.court, 0) + 1
        line = {"mode": "committed" if args.commit else "preview", **record.preview()}
        try:
            if args.commit:
                with session_factory() as db:
                    try:
                        outcome, authority_id = persist_record(db, record, retrieved_at)
                        db.commit()
                    except Exception:
                        db.rollback()
                        raise
                line.update(outcome=outcome, authority_id=authority_id)
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
        except Exception as exc:
            failed += 1
            state.setdefault("failed_clusters", []).append(record.meta.cluster_id)
            line = {"mode": "error", "cluster_id": record.meta.cluster_id, "error_type": type(exc).__name__}
        if not args.quiet:
            print(json.dumps(line), flush=True)
        handled += 1
        if handled >= args.limit:
            break
    if args.commit:  # a preview never advances the commit checkpoint
        _save_state(args.state_file, state)
    print(json.dumps({"summary": True, **header, "matched": matched, "offset": args.offset, "handled": handled,
                      "by_court": by_court, "failed": failed, "outcomes": outcomes,
                      "rows_scanned": state.get("rows_scanned"), "skips": state.get("counts", {}),
                      "committed": args.commit, "seconds": round(time.time() - started, 1)}), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
