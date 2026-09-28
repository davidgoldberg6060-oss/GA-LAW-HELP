"""Operator-run, resumable import of Supreme Court of Georgia opinion PDFs.

The court's annual opinion pages are the discovery source. A successful
container or index fetch is never counted as a committed authority. Run in
preview mode first, then explicitly pass --commit after reviewing the output.
This importer covers the court's online opinion archive, not all Georgia cases.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import json
import re
import time
from urllib.parse import urljoin, urlparse

from .http_transport import production_transport
from .import_one import prepare
from .security import assert_public_official_url
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
    return list({item.url: item for item in parser.opinions}.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--limit", type=int, default=25, help="Maximum PDFs per run (1-100)")
    parser.add_argument("--pause", type=float, default=2.0, help="Seconds between court requests")
    parser.add_argument("--commit", action="store_true", help="Persist each validated document")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 100 or not 0.5 <= args.pause <= 30:
        parser.error("Limit must be 1-100 and pause must be 0.5-30 seconds")
    opinions = discover(args.year)
    success = 0
    errors = 0
    for opinion in opinions[:args.limit]:
        try:
            item = prepare("ga_supreme_opinions", opinion.url, opinion.title, opinion.docket)
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
                              "docket": opinion.docket, "authority_id": authority_id,
                              "source_url": opinion.url}), flush=True)
        except Exception as exc:
            errors += 1
            print(json.dumps({"mode": "error", "year": args.year, "docket": opinion.docket,
                              "error_type": type(exc).__name__}), flush=True)
        time.sleep(args.pause)
    print(json.dumps({"year": args.year, "discovered": len(opinions),
                      "attempted": min(len(opinions), args.limit), "succeeded": success,
                      "failed": errors, "committed": args.commit}), flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
