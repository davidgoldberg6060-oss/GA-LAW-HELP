#!/usr/bin/env python3
"""Versioned Georgia statutes ingestion pipeline for GA.LAW.HELP.

Imports PUBLIC Georgia statutory material from explicitly configured verified
sources into normalized JSONL records for the internal legal corpus.

Safety/integrity rules:
- Never invent a code section, title, effective date, or source URL.
- Preserve source text and SHA-256 so later amendments can be detected.
- Keep effective/repealed/superseded metadata nullable until verified.
- Historical versions remain separate records instead of being overwritten.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

USER_AGENT = "GA.LAW.HELP-public-legal-corpus/1.0"

@dataclass
class StatuteRecord:
    jurisdiction: str
    authority_type: str
    citation: str | None
    title_number: str | None
    chapter_number: str | None
    section_number: str | None
    heading: str | None
    text: str
    source_url: str
    retrieved_at: str
    content_sha256: str
    effective_date: str | None
    end_date: str | None
    status: str
    verification_status: str


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(charset, errors="replace")


def plain(raw: str) -> str:
    raw = re.sub(r"(?is)<script.*?>.*?</script>|<style.*?>.*?</style>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize(url: str, raw: str) -> StatuteRecord:
    text = plain(raw)
    # Do not infer individual section numbers from an index/snapshot. A later
    # source-specific parser segments only when the source exposes them clearly.
    return StatuteRecord(
        jurisdiction="Georgia",
        authority_type="statute",
        citation=None,
        title_number=None,
        chapter_number=None,
        section_number=None,
        heading=None,
        text=text,
        source_url=url,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        content_sha256=digest(text),
        effective_date=None,
        end_date=None,
        status="source_snapshot_pending_section_segmentation",
        verification_status="source_verified_record_pending_citation_parse",
    )


def configured_sources(path: Path) -> list[str]:
    if not path.exists(): return []
    data = json.loads(path.read_text(encoding="utf-8"))
    urls=[]
    for s in data.get("sources", []):
        category=(s.get("category") or "").lower()
        name=(s.get("name") or "").lower()
        if s.get("enabled", True) and (category in {"statutes","code","legislation"} or "georgia code" in name):
            if s.get("url"): urls.append(s["url"])
    return urls


def ingest(urls: Iterable[str]) -> list[StatuteRecord]:
    return [normalize(url, fetch(url)) for url in urls]


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--source", action="append", default=[])
    p.add_argument("--sources-file", default="data/legal_sources.json")
    p.add_argument("--output", default="data/corpus/georgia_statutes.jsonl")
    a=p.parse_args()
    urls=list(a.source) or configured_sources(Path(a.sources_file))
    if not urls:
        raise SystemExit("No verified Georgia statute source configured; refusing to guess a source.")
    records=ingest(urls)
    out=Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in records: f.write(json.dumps(asdict(r), ensure_ascii=False)+"\n")
    print(f"Wrote {len(records)} statute source snapshots to {out}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
