"""Authoritative-source acquisition adapters for Georgia corpus ingestion.

Verified authority ingestion still requires source-backed citation evidence.
For corpus-expansion jobs, callers may explicitly retain an official public
source document under a clearly labeled docket/document identifier when a
reporter citation is not yet available. That fallback is searchable data, not
a representation that the identifier is a legal citation or current authority.
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
    allow_unverified_identifier: bool = False,
) -> IngestionItem:
    """Acquire one approved official document.

    Normal authority ingestion requires a source-published citation. Bulk corpus
    jobs may opt in to ``allow_unverified_identifier``. In that mode, an
    official document with no reporter citation is retained using its source
    identifier, explicitly labeled as an unverified document identifier. The
    underlying LegalStatus remains unverified/unknown, so grounded analysis can
    distinguish it from verified/current authority.
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
    if not citation and allow_unverified_identifier:
        identifier=(request.external_id or "").strip()
        if not identifier:
            raise ValueError(
                "Official document acquired without citation or stable source identifier; "
                "record cannot be indexed safely."
            )
        citation=f"{identifier} [UNVERIFIED DOCUMENT ID]"
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
    allow_unverified_identifier: bool = False,
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
                    allow_unverified_identifier=allow_unverified_identifier,
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
