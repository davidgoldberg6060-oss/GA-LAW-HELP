"""Secure acquisition primitives for official Georgia legal documents.

This layer validates provenance and response integrity before constructing a
SourceDocument. It intentionally does not extract or invent legal citations.
Network transport is injected so production can use a hardened HTTP client and
tests can remain deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

from .adapters import legal_status_from_official_text
from .models import SourceDocument
from .pipeline import source_for
from .security import assert_public_official_url

MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "text/html",
    "text/plain",
    "application/pdf",
    "application/xhtml+xml",
}


@dataclass(frozen=True)
class FetchResponse:
    url: str
    status_code: int
    headers: Mapping[str, str]
    body: bytes


Transport = Callable[[str], FetchResponse]


def _content_type(headers: Mapping[str, str]) -> str:
    raw = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
    return raw.split(";", 1)[0].strip().lower()


def acquire_official_document(
    *,
    source_key: str,
    url: str,
    title: str,
    transport: Transport,
    external_id: str | None = None,
    retrieved_at: datetime | None = None,
) -> SourceDocument:
    """Fetch and validate one document from a registered official Georgia source."""
    source = source_for(source_key)
    requested_url = assert_public_official_url(url)
    response = transport(requested_url)

    # Revalidate the final URL to prevent a trusted host redirecting acquisition
    # to an unapproved host or non-HTTPS destination.
    final_url = assert_public_official_url(response.url)
    if response.status_code != 200:
        raise ValueError(f"Official source returned HTTP {response.status_code}")
    if not response.body:
        raise ValueError("Official source returned an empty document")
    if len(response.body) > MAX_DOCUMENT_BYTES:
        raise ValueError("Official document exceeds ingestion size limit")

    content_type = _content_type(response.headers)
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported official document content type: {content_type or 'missing'}")

    checked_at = retrieved_at or datetime.now(timezone.utc)
    # Status extraction is only meaningful for textual material. PDFs remain
    # unknown until a separate trusted parser supplies explicit status evidence.
    if content_type in {"text/html", "text/plain", "application/xhtml+xml"}:
        text = response.body.decode("utf-8", errors="replace")
        legal_status = legal_status_from_official_text(text, final_url, checked_at=checked_at)
    else:
        from .models import LegalStatus
        legal_status = LegalStatus(
            verification_status="official",
            status_checked_at=checked_at,
            status_source_url=final_url,
        )

    return SourceDocument(
        source_key=source.key,
        url=final_url,
        title=title.strip() or source.title,
        body=response.body,
        retrieved_at=checked_at,
        external_id=external_id,
        content_type=content_type,
        metadata={"authority_type": source.authority_type, "jurisdiction": source.jurisdiction},
        legal_status=legal_status,
    )
