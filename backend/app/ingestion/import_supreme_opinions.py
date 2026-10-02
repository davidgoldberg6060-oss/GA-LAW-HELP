"""Operator-run, resumable import of Supreme Court of Georgia opinion PDFs.

The court's annual opinion pages are the discovery source. Reporter citations
are used when deterministically found in the official PDF. For corpus expansion,
an opinion without a reporter citation is still retained under a clearly marked
UNVERIFIED DOCUMENT ID based on the court docket; it must not be represented as
verified/current authority until later evidence upgrades it.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import json
import os
import re
import time
from urllib.parse import urljoin, urlparse

from .http_transport import production_transport
from .pdf_evidence import resolve_official_pdf_georgia_citation
from .security import assert_public_official_url
from .source_acquisition import OfficialDocumentRequest, acquire_ingestion_item
from ..database import SessionLocal
from .pipeline import persist_item

CASE_NO = re.compile(r"\bS\d{2}[A-Z]\d{4}\b", re.I)
INDEX_LIMIT = 3 * 1024 * 1024


@dataclass(frozen=True)
class Opinion:
    docket: str
    title: str
    url: str


class OpinionIndex(HTMLParser):
    def __init__(self, index_url: str):
        super().__init__(convert_charrefs=True)
        self.index_url = index_url
        self.current_href: str | None = None
        self.current_text: list[str] = []
        self.opinions: list[Opinion] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data):
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag != "a" or self.current_href is None:
            return
        label = " ".join(" ".join(self.current_text).split())
        match = CASE_NO.search(label)
        url = urljoin(self.index_url, self.current_href)
        if match and urlparse(url).path.lower().endswith(".pdf"):
            try:
                assert_public_official_url(url)
            except ValueError:
                pass
            else:
                if urlparse(url).hostname in {"gasupreme.us", "www.gasupreme.us"}:
                    self.opinions.append(Opinion(match.group().upper(), label, url))
        self.current_href = None
        self.current_text = []


def _validated_unique_opinions(opinions: list[Opinion]) -> list[Opinion]:
    """Deduplicate repeated links but reject conflicting provenance for a docket."""
    by_url: dict[str, Opinion] = {}
    docket_urls: dict[str, set[str]] = {}
    for item in opinions:
        by_url.setdefault(item.url, item)
        docket_urls.setdefault(item.docket, set()).add(item.url)
    conflicts = sorted(docket for docket, urls in docket_urls.items() if len(urls) > 1)
    if conflicts:
        raise ValueError("Ambiguous court index: docket appears at multiple PDF URLs: " + ", ".join(conflicts))
    return list(by_url.values())


def discover(year: int, transport=production_transport) -> list[Opinion]:
    if not 2017 <= year <= 2100:
        raise ValueError("Select a year in the court's published online archive")
    index_url = f"https://www.gasupreme.us/{year}-opinions/"
    response = transport(index_url)
    if response.status_code != 200 or len(response.body) > INDEX_LIMIT:
        raise ValueError(f"Unable to read bounded court index for {year}")
    if urlparse(response.url).hostname not in {"gasupreme.us", "www.gasupreme.us"}:
        raise ValueError("Court index redirected outside the court host")
    content_type = next((v for k, v in response.headers.items() if k.lower() == "content-type"), "")
    if not content_type.lower().startswith("text/html"):
        raise ValueError("Court index did not return HTML")
    parser = OpinionIndex(index_url)
    parser.feed(response.body.decode("utf-8", errors="replace"))
    if not parser.opinions:
        raise ValueError("No opinion PDFs discovered; inspect the index layout")
    return _validated_unique_opinions(parser.opinions)


def prepare_opinion(opinion: Opinion, *, transport=production_transport):
    """Acquire one opinion; retain docket-labeled data if reporter citation is absent."""
    request = OfficialDocumentRequest(
        source_key="ga_supreme_opinions",
        url=opinion.url,
        title=opinion.title,
        external_id=opinion.docket,
    )
    return acquire_ingestion_item(
        request,
        transport=transport,
        citation_resolver=resolve_official_pdf_georgia_citation,
        allow_unverified_identifier=True,
    )


def commit_database_ready() -> bool:
    """--commit may persist only when an explicit non-sqlite DATABASE_URL is set.

    The app defaults to a local sqlite file when DATABASE_URL is unset. That
    fallback must not be treated as the Georgia legal corpus.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return False
    return not url.lower().startswith("sqlite")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--limit", type=int, default=100, help="Maximum PDFs per run (1-500)")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many index entries for a later batch")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds between court requests")
    parser.add_argument("--commit", action="store_true", help="Persist each acquired document")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 500 or args.offset < 0 or not 0.5 <= args.pause <= 30:
        parser.error("Limit must be 1-500, offset nonnegative, and pause 0.5-30 seconds")
    if args.commit and not commit_database_ready():
        print(json.dumps({
            "year": args.year,
            "committed": False,
            "reason": "DATABASE_URL is unset or is the local sqlite fallback; refusing --commit so no corpus rows are invented",
            "discovered": None,
            "attempted": 0,
            "succeeded": 0,
            "failed": 0,
        }), flush=True)
        return 2
    opinions = discover(args.year)
    success = 0
    errors = 0
    unverified = 0
    batch = opinions[args.offset:args.offset + args.limit]
    for opinion in batch:
        try:
            item = prepare_opinion(opinion)
            is_unverified_id = item.citation.endswith("[UNVERIFIED DOCUMENT ID]")
            if is_unverified_id:
                unverified += 1
            if args.commit:
                with SessionLocal() as db:
                    try:
                        saved = persist_item(db, item)
                        db.commit()
                        authority_id = saved.id
                    except Exception:
                        db.rollback()
                        raise
            else:
                authority_id = None
            success += 1
            print(json.dumps({"mode": "committed" if args.commit else "preview", "year": args.year,
                              "docket": opinion.docket, "citation": item.citation,
                              "unverified_identifier": is_unverified_id,
                              "authority_id": authority_id, "source_url": opinion.url}), flush=True)
        except Exception as exc:
            errors += 1
            print(json.dumps({"mode": "error", "year": args.year, "docket": opinion.docket,
                              "error_type": type(exc).__name__}), flush=True)
        time.sleep(args.pause)
    print(json.dumps({"year": args.year, "discovered": len(opinions), "offset": args.offset,
                      "attempted": len(batch), "succeeded": success, "unverified": unverified,
                      "failed": errors, "committed": args.commit}), flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
