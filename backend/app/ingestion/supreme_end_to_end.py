"""Conservative Supreme Court of Georgia discovery-to-acquisition bridge.

Discovery metadata is never promoted to legal authority by itself. Each opinion
must pass official-document acquisition and independently obtain a
source-published citation before it can become an IngestionItem.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .acquisition import Transport
from .pipeline import IngestionItem
from .source_acquisition import CitationResolver, acquire_ingestion_item
from .supreme_listing import DiscoveredSupremeOpinion, discover_supreme_opinions


@dataclass(frozen=True)
class SupremeAcquisitionResult:
    items: tuple[IngestionItem, ...]
    skipped: tuple[dict, ...]


def acquire_discovered_supreme_opinions(
    page_html: str,
    *,
    page_url: str,
    transport: Transport,
    citation_resolver: CitationResolver | None = None,
    limit: int = 100,
) -> SupremeAcquisitionResult:
    """Discover and acquire a bounded batch without inventing reporter citations."""
    if limit < 1 or limit > 500:
        raise ValueError("Supreme Court acquisition limit must be between 1 and 500")

    discovered = discover_supreme_opinions(page_html, page_url=page_url)[:limit]
    items: list[IngestionItem] = []
    skipped: list[dict] = []

    for opinion in discovered:
        try:
            items.append(
                acquire_ingestion_item(
                    opinion.as_request(),
                    transport=transport,
                    citation_resolver=citation_resolver,
                )
            )
        except (ValueError, UnicodeError) as exc:
            skipped.append(
                {
                    "docket_numbers": list(opinion.docket_numbers),
                    "url": opinion.url,
                    "reason": str(exc),
                }
            )

    return SupremeAcquisitionResult(tuple(items), tuple(skipped))
