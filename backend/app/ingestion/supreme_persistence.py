"""Transactional Supreme Court discovery, evidence, and persistence boundary."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from .acquisition import Transport
from .pipeline import persist_batch
from .source_acquisition import CitationResolver
from .supreme_end_to_end import acquire_discovered_supreme_opinions


@dataclass(frozen=True)
class SupremePersistenceResult:
    discovered_for_index: int
    persisted: int
    skipped: tuple[dict, ...]


def acquire_and_persist_supreme_opinions(
    db: Session,
    page_html: str,
    *,
    page_url: str,
    transport: Transport,
    citation_resolver: CitationResolver | None = None,
    limit: int = 100,
) -> SupremePersistenceResult:
    """Persist only Supreme Court opinions that pass every evidence gate.

    Acquisition failures remain skipped. Qualifying items are handed to the
    existing atomic persistence batch, so a database/persistence failure rolls
    back the entire qualifying batch rather than leaving a partial index.
    """
    acquired = acquire_discovered_supreme_opinions(
        page_html,
        page_url=page_url,
        transport=transport,
        citation_resolver=citation_resolver,
        limit=limit,
    )
    if not acquired.items:
        return SupremePersistenceResult(0, 0, acquired.skipped)

    saved = persist_batch(db, acquired.items)
    return SupremePersistenceResult(len(acquired.items), len(saved), acquired.skipped)
