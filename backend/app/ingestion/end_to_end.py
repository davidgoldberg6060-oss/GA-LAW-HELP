"""End-to-end official Georgia authority import.

A citation must come from the official source/caller. This workflow does not
infer or fabricate legal citations.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from .acquisition import Transport, acquire_official_document
from .http_transport import production_transport
from .jobs import ingest_verified_batch
from .pipeline import source_for


def acquire_and_persist(
    db: Session,
    *,
    source_key: str,
    url: str,
    title: str,
    citation: str,
    external_id: str | None = None,
    transport: Transport = production_transport,
):
    """Acquire, validate and persist one official Georgia legal authority."""
    citation = (citation or "").strip()
    if not citation:
        raise ValueError("A citation published by the official source is required.")

    # Resolve the registry entry before network I/O so unsupported sources fail
    # closed without making an outbound request.
    source_for(source_key)
    document = acquire_official_document(
        source_key=source_key,
        url=url,
        title=title,
        external_id=external_id,
        transport=transport,
    )
    saved = ingest_verified_batch(db, [(source_key, document, citation)])
    return saved[0]


def acquire_and_persist_batch(db: Session, records: list[dict], *, transport: Transport = production_transport):
    """Acquire a mixed official batch, then persist it atomically.

    Acquisition completes before database persistence begins. If any source,
    document, or citation fails validation, no record from the batch is written.
    """
    acquired = []
    for record in records:
        source_key = str(record.get("source_key", "")).strip()
        citation = str(record.get("citation", "")).strip()
        if not citation:
            raise ValueError("Every authority requires a citation published by its official source.")
        source_for(source_key)
        document = acquire_official_document(
            source_key=source_key,
            url=str(record.get("url", "")).strip(),
            title=str(record.get("title", "")).strip(),
            external_id=record.get("external_id"),
            transport=transport,
        )
        acquired.append((source_key, document, citation))
    return ingest_verified_batch(db, acquired)
