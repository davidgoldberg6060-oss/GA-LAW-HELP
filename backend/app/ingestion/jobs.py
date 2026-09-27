"""Guarded entry points for importing Georgia legal material into the corpus.

Network acquisition stays separate from persistence. A caller must provide a
SourceDocument produced from an approved official source and the citation
published by that source. These jobs deliberately do not guess citations.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from .models import SourceDocument
from .pipeline import IngestionItem, persist_batch, persist_item, source_for


def _item(source_key: str, document: SourceDocument, citation: str) -> IngestionItem:
    source = source_for(source_key)
    return IngestionItem(
        source_name=source.key,
        document=document,
        jurisdiction=source.jurisdiction,
        authority_type=source.authority_type,
        citation=citation,
    )


def ingest_georgia_code(db: Session, document: SourceDocument, citation: str):
    """Persist an O.C.G.A. authority only when its official citation is supplied."""
    return persist_item(db, _item("ga_code", document, citation))


def ingest_georgia_legislation(db: Session, document: SourceDocument, citation: str):
    return persist_item(db, _item("ga_legislation", document, citation))


def ingest_georgia_court_rule(db: Session, document: SourceDocument, citation: str):
    return persist_item(db, _item("ga_court_rules", document, citation))


def ingest_supreme_court_rule(db: Session, document: SourceDocument, citation: str):
    return persist_item(db, _item("ga_supreme_rules", document, citation))


def ingest_supreme_court_opinion(db: Session, document: SourceDocument, citation: str):
    return persist_item(db, _item("ga_supreme_opinions", document, citation))


def ingest_court_of_appeals_opinion(db: Session, document: SourceDocument, citation: str):
    return persist_item(db, _item("ga_appeals_opinions", document, citation))


def ingest_verified_batch(db: Session, records: list[tuple[str, SourceDocument, str]]):
    """Atomically persist mixed official Georgia authorities."""
    return persist_batch(db, [_item(source_key, document, citation) for source_key, document, citation in records])
