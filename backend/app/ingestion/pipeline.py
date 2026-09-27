"""End-to-end Georgia legal ingestion pipeline.

Connects approved-source adapters to conservative LegalAuthority persistence.
Nothing is persisted unless the caller supplies a real citation. The pipeline
never derives or fabricates a citation from page text.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session

from .adapters import ADAPTERS
from .models import SourceDocument
from .persistence import upsert_authority_document


@dataclass(frozen=True)
class IngestionItem:
    source_name: str
    document: SourceDocument
    jurisdiction: str
    authority_type: str
    citation: str


def persist_item(db: Session, item: IngestionItem):
    citation = (item.citation or "").strip()
    if not citation:
        raise ValueError("A verified citation is required before legal material may enter the authority index.")
    if item.source_name not in ADAPTERS:
        raise ValueError(f"Unsupported Georgia ingestion source: {item.source_name}")
    return upsert_authority_document(
        db,
        document=item.document,
        jurisdiction=item.jurisdiction,
        authority_type=item.authority_type,
        citation=citation,
    )


def persist_batch(db: Session, items: Iterable[IngestionItem]) -> list:
    """Persist one atomic batch; rollback everything if any record is invalid."""
    saved = []
    try:
        for item in items:
            saved.append(persist_item(db, item))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return saved


def adapter_for(source_name: str):
    """Return only an explicitly approved Georgia source adapter."""
    try:
        return ADAPTERS[source_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported Georgia ingestion source: {source_name}") from exc
