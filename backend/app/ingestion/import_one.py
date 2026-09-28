"""Operator-run import of one verified, textual Georgia legal authority.

Run as: python -m app.ingestion.import_one --source ga_code --url URL
    --title TITLE --citation CITATION [--commit]

A preview is the default. No background worker or public API invokes this tool.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from hashlib import sha256
from html.parser import HTMLParser
from io import BytesIO
import json
import os

from pypdf import PdfReader
from urllib.parse import urlparse

from .acquisition import acquire_official_document
from .http_transport import production_transport
from .pipeline import persist_item, IngestionItem, source_for
from ..database import SessionLocal


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def _visible_text(body: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        if not body.startswith(b"%PDF-") or len(body) > 8 * 1024 * 1024:
            raise ValueError("Unsupported or oversized PDF")
        try:
            reader = PdfReader(BytesIO(body), strict=True)
            if reader.is_encrypted or not 0 < len(reader.pages) <= 300:
                raise ValueError("Encrypted, empty, or oversized PDF")
            parts = []
            total = 0
            for page in reader.pages:
                page_text = page.extract_text() or ""
                total += len(page_text)
                if total > 2_000_000:
                    raise ValueError("Extracted PDF text exceeds size limit")
                parts.append(page_text)
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Unable to extract official PDF text") from exc
        text = "\n".join(parts).strip()
        if len(text) < 50:
            raise ValueError("PDF has no usable searchable text; manual OCR review required")
        return text
    text = body.decode("utf-8", errors="replace")
    if content_type in {"text/html", "application/xhtml+xml"}:
        parser = _VisibleText()
        parser.feed(text)
        return " ".join(parser.parts)
    return text


def prepare(source_key: str, url: str, title: str, citation: str):
    source = source_for(source_key)
    if not citation or not citation.strip():
        raise ValueError("A source verified citation is required")
    # A registered host alone does not establish the document's source type.
    expected_host = urlparse(source.url).hostname
    allowed_hosts = {expected_host}
    if source_key in {"ga_court_rules", "ga_supreme_rules"}:
        allowed_hosts.add("assets.georgiacourts.gov")
    if urlparse(url).hostname not in allowed_hosts:
        raise ValueError("Document host does not match the selected source")
    if url.rstrip("/") == source.url.rstrip("/"):
        raise ValueError("Select an individual authority document, not a source index")

    document = acquire_official_document(
        source_key=source_key, url=url, title=title,
        transport=production_transport,
    )
    if urlparse(document.url).hostname not in allowed_hosts:
        raise ValueError("Redirect changed the selected source host")
    if document.content_type not in {"text/html", "text/plain", "application/xhtml+xml", "application/pdf"}:
        raise ValueError("Unsupported authority document format")
    normalized_text = " ".join(_visible_text(document.body, document.content_type).split())
    normalized_citation = " ".join(citation.split())
    if normalized_citation.casefold() not in normalized_text.casefold():
        raise ValueError("Citation is absent from the official document text")
    # A page-wide keyword match does not prove that this specific authority is
    # current or repealed. Preserve provenance but defer status adjudication.
    document = replace(
        document,
        extracted_text=normalized_text,
        legal_status=replace(
            document.legal_status,
            currency_status="unknown",
            precedential_status="unknown",
            negative_treatment=(),
        ),
    )
    return IngestionItem(
        source_name=source.key, document=document,
        jurisdiction=source.jurisdiction,
        authority_type=source.authority_type,
        citation=normalized_citation,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--citation", required=True)
    parser.add_argument("--commit", action="store_true", help="Write to the authority database")
    args = parser.parse_args(argv)

    item = prepare(args.source, args.url, args.title, args.citation)
    if args.commit:
        database_url = os.getenv("DATABASE_URL", "")
        if os.getenv("ENVIRONMENT", "").lower() == "production":
            if not database_url.startswith("postgresql") or "sslmode=" not in database_url:
                raise RuntimeError("Production import requires PostgreSQL with SSL")
        with SessionLocal() as db:
            try:
                authority = persist_item(db, item)
                db.commit()
                authority_id = authority.id
            except Exception:
                db.rollback()
                raise
    else:
        authority_id = None

    print(json.dumps({
        "mode": "committed" if args.commit else "preview",
        "authority_id": authority_id,
        "source": item.source_name,
        "citation": item.citation,
        "url": item.document.url,
        "sha256": sha256(item.document.body).hexdigest(),
        "retrieved_at": item.document.retrieved_at.isoformat(),
        "currency_status": item.document.legal_status.currency_status,
        "precedential_status": item.document.legal_status.precedential_status,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
