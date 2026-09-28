"""Normalize acquired Georgia legal documents without inventing legal facts."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .models import SourceDocument

_OCGA = re.compile(r"\bO\.?C\.?G\.?A\.?\s*(?:§|section)?\s*(\d{1,2}-\d{1,3}-\d+(?:\.\d+)?)\b", re.I)
_CASE_NO = re.compile(r"\b(?:S\d{2}[A-Z]\d{4}|A\d{2}A\d{4})\b")
_WS = re.compile(r"\s+")


@dataclass(frozen=True)
class NormalizedAuthority:
    source_key: str
    title: str
    url: str
    text: str
    citation_candidates: tuple[str, ...]
    external_id: str | None
    authority_type: str
    jurisdiction: str


def _decode_text(document: SourceDocument) -> str:
    content_type = (document.content_type or "").lower()
    if content_type == "application/pdf":
        raise ValueError("PDF normalization requires the trusted PDF extraction stage")
    if content_type not in {"text/html", "text/plain", "application/xhtml+xml"}:
        raise ValueError("Unsupported document type for text normalization")
    return document.body.decode("utf-8", errors="replace")


def _visible_text(raw: str) -> str:
    # Deliberately modest HTML cleanup. This is not a legal citation parser and
    # must not infer holdings, status, or citations that are absent from source.
    raw = re.sub(r"(?is)<(?:script|style)\b.*?>.*?</(?:script|style)>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return _WS.sub(" ", raw).strip()


def normalize_authority(document: SourceDocument) -> NormalizedAuthority:
    text = _visible_text(_decode_text(document))
    candidates: list[str] = []
    for match in _OCGA.finditer(text):
        citation = f"O.C.G.A. § {match.group(1)}"
        if citation not in candidates:
            candidates.append(citation)
    for match in _CASE_NO.finditer(text):
        citation = match.group(0)
        if citation not in candidates:
            candidates.append(citation)

    return NormalizedAuthority(
        source_key=document.source_key,
        title=document.title,
        url=document.url,
        text=text,
        citation_candidates=tuple(candidates),
        external_id=document.external_id,
        authority_type=str(document.metadata.get("authority_type", "unknown")),
        jurisdiction=str(document.metadata.get("jurisdiction", "Georgia")),
    )
