"""Authoritative-source acquisition adapters for Georgia corpus ingestion.

These adapters deliberately stop before persistence when a source does not
publish a citation or other required evidence. They never synthesize legal
citations from titles, docket numbers, URLs, or model output.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from .acquisition import Transport, acquire_official_document
from .models import SourceDocument
from .pipeline import IngestionItem, source_for


@dataclass(frozen=True)
class OfficialDocumentRequest:
    source_key: str
    url: str
    title: str
    citation: str | None = None
    external_id: str | None = None


CitationResolver = Callable[[SourceDocument], str | None]


def acquire_ingestion_item(
    request: OfficialDocumentRequest,
    *,
    transport: Transport,
    citation_resolver: CitationResolver | None = None,
    retrieved_at: datetime | None = None,
) -> IngestionItem:
    """Acquire one approved official document and require source-backed citation evidence.

    A citation may be supplied by a source listing/parser that already extracted
    the source-published citation, or by a deterministic resolver operating on
    the acquired official document. Missing evidence is a hard stop.
    """
    source = source_for(request.source_key)
    document = acquire_official_document(
        source_key=source.key,
        url=request.url,
        title=request.title,
        transport=transport,
        external_id=request.external_id,
        retrieved_at=retrieved_at,
    )
    citation=(request.citation or "").strip()
    if not citation and citation_resolver is not None:
        citation=(citation_resolver(document) or "").strip()
    if not citation:
        raise ValueError(
            "Official document acquired, but no source-published citation was available; "
            "record was not admitted to the legal authority index."
        )
    return IngestionItem(
        source_name=source.key,
        document=document,
        jurisdiction=source.jurisdiction,
        authority_type=source.authority_type,
        citation=citation,
    )


def acquire_many(
    requests: list[OfficialDocumentRequest],
    *,
    transport: Transport,
    citation_resolver: CitationResolver | None = None,
) -> tuple[list[IngestionItem], list[dict]]:
    """Acquire a bounded source batch while isolating bad/unverifiable records."""
    items: list[IngestionItem]=[]
    skipped: list[dict]=[]
    for request in requests:
        try:
            items.append(
                acquire_ingestion_item(
                    request,
                    transport=transport,
                    citation_resolver=citation_resolver,
                )
            )
        except (ValueError, UnicodeError) as exc:
            skipped.append({
                "source_key": request.source_key,
                "url": request.url,
                "external_id": request.external_id,
                "reason": str(exc),
            })
    return items, skipped
