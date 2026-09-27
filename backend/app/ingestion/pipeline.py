"""End-to-end Georgia legal ingestion pipeline.

Connects approved first-party Georgia source definitions to conservative
LegalAuthority persistence. Nothing is persisted unless the caller supplies a
real citation; this module never invents one from page text.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session

from .adapters import AuthoritySource, official_georgia_authority_sources
from .models import SourceDocument
from .persistence import upsert_authority_document


def _source_registry() -> dict[str, AuthoritySource]:
    return {source.key: source for source in official_georgia_authority_sources()}


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

    source = _source_registry().get(item.source_name)
    if source is None:
        raise ValueError(f"Unsupported Georgia ingestion source: {item.source_name}")
    if item.jurisdiction.strip().lower() != source.jurisdiction.lower():
        raise ValueError("Ingestion jurisdiction does not match the approved source registry.")
    if item.authority_type.strip().lower() != source.authority_type.lower():
        raise ValueError("Authority type does not match the approved source registry.")

    return upsert_authority_document(
        db,
        document=item.document,
        jurisdiction=source.jurisdiction,
        authority_type=source.authority_type,
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


def source_for(source_name: str) -> AuthoritySource:
    """Return only a registered, revalidated first-party Georgia source."""
    try:
        return _source_registry()[source_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported Georgia ingestion source: {source_name}") from exc
