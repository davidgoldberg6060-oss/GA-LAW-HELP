#!/usr/bin/env python3
"""Georgia Court of Appeals ingestion pipeline for GA.LAW.HELP.

Collects PUBLIC appellate opinion metadata/content from configured authoritative
sources, normalizes it, hashes it, and emits records for the internal legal
corpus. This module deliberately does not guess missing opinions or fabricate
citations. Unavailable/restricted records remain unavailable.

Configure source URLs in data/legal_sources.json or pass --source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

USER_AGENT = "GA.LAW.HELP-public-legal-corpus/1.0"

@dataclass
class OpinionRecord:
    court: str
    jurisdiction: str
    title: str
    docket_number: str | None
    decision_date: str | None
    source_url: str
    source_type: str
    status: str
    retrieved_at: str
    content_sha256: str
    text: str


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def strip_html(raw: str) -> str:
    raw = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style.*?>.*?</style>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_source(url: str, raw: str) -> OpinionRecord:
    text = strip_html(raw)
    # Conservative metadata extraction only. The corpus enrichment stage can
    # parse individual opinion links/dockets after source-specific verification.
    title_match = re.search(r"(?i)(Georgia Court of Appeals[^|<]*)", raw)
    title = strip_html(title_match.group(1)) if title_match else "Georgia Court of Appeals public opinions"
    return OpinionRecord(
        court="Court of Appeals of Georgia",
        jurisdiction="Georgia",
        title=title[:500],
        docket_number=None,
        decision_date=None,
        source_url=url,
        source_type="official_public_source",
        status="source_snapshot_pending_opinion_segmentation",
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        content_sha256=sha256(text),
        text=text,
    )


def load_configured_sources(path: Path) -> list[str]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    values: list[str] = []
    for source in data.get("sources", []):
        if source.get("enabled", True) and source.get("category") in {"case_law", "court_opinions"}:
            if "appeal" in (source.get("name", "") + source.get("court", "")).lower():
                url = source.get("url")
                if url:
                    values.append(url)
    return values


def ingest(urls: Iterable[str]) -> list[OpinionRecord]:
    records = []
    for url in urls:
        raw = fetch_text(url)
        records.append(normalize_source(url, raw))
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", default=[], help="Authoritative public source URL; repeatable")
    parser.add_argument("--sources-file", default="data/legal_sources.json")
    parser.add_argument("--output", default="data/corpus/georgia_court_of_appeals.jsonl")
    args = parser.parse_args()

    urls = list(args.source) or load_configured_sources(Path(args.sources_file))
    if not urls:
        raise SystemExit("No Court of Appeals source configured. Add a verified public source; ingestion will not guess one.")

    records = ingest(urls)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} verified-source snapshots to {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
