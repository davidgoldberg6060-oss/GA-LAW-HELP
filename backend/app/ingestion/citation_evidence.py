"""Citation-evidence gates for Georgia legal corpus admission.

Reporter citations are accepted only from textual documents acquired from an
approved official source. PDF bytes are intentionally not decoded here; a
trusted PDF text extractor must provide explicit text evidence separately.
"""
from __future__ import annotations

from .models import SourceDocument
from .pipeline import source_for
from .reporter_citation import resolve_single_georgia_reporter_citation

_TEXT_TYPES={"text/html","text/plain","application/xhtml+xml"}


def resolve_official_georgia_citation(document: SourceDocument) -> str | None:
    """Return one unambiguous Georgia Reports citation from official source text."""
    source=source_for(document.source_key)
    if source.jurisdiction.strip().lower() != "georgia":
        return None
    if document.content_type not in _TEXT_TYPES:
        return None
    if document.legal_status is None or document.legal_status.verification_status != "official":
        return None
    try:
        text=document.body.decode("utf-8",errors="strict")
    except UnicodeDecodeError:
        return None
    return resolve_single_georgia_reporter_citation(text)
