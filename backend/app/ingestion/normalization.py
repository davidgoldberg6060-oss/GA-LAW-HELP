"""Normalize acquired Georgia legal documents without inventing legal facts."""
from __future__ import annotations

import html
import re
from dataclasses import dataclass

from .models import SourceDocument

# Capture only identifiers actually present in source text.  Formatting is
# canonicalized so ingestion and native lookup use the same stable values.
_OCGA = re.compile(r"\b(?:O\.?\s*C\.?\s*G\.?\s*A\.?|OCGA)\s*(?:(?:§|section)\s*)?(\d{1,2}\s*-\s*\d{1,3}\s*-\s*\d+(?:\.\d+)?)\b", re.I)
_CASE_NO = re.compile(r"\b(?:S\s*\d{2}\s*[A-Z]\s*\d{4}|A\s*\d{2}\s*A\s*\d{4})\b", re.I)
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
    content_type = (document.content_type or "").split(";", 1)[0].strip().lower()
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
    return _WS.sub(" ", html.unescape(raw)).strip()


def _canonical_section(value: str) -> str:
    return re.sub(r"\s*-\s*", "-", value.strip())


def _canonical_case_number(value: str) -> str:
    return re.sub(r"\s+", "", value).upper()


def normalize_authority(document: SourceDocument) -> NormalizedAuthority:
    text = _visible_text(_decode_text(document))
    candidates: list[str] = []
    for match in _OCGA.finditer(text):
        citation = f"O.C.G.A. § {_canonical_section(match.group(1))}"
        if citation not in candidates:
            candidates.append(citation)
    for match in _CASE_NO.finditer(text):
        citation = _canonical_case_number(match.group(0))
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
