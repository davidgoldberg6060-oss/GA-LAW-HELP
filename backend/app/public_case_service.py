"""Public Georgia case-law projection.

This module deliberately accepts LegalAuthority records only. User-owned Case,
Evidence, CaseNote, and TimelineEvent records must never enter this projection.
"""
from urllib.parse import urlparse

EXCLUDED_PUBLIC_STATUSES = {
    "sealed",
    "juvenile",
    "expunged",
    "restricted",
    "private",
    "unavailable",
}


def is_public_georgia_case(authority) -> bool:
    jurisdiction = str(getattr(authority, "jurisdiction", "") or "").strip().lower()
    authority_type = str(getattr(authority, "authority_type", "") or "").strip().lower()
    status = str(getattr(authority, "status", "") or "").strip().lower()
    return (
        "georgia" in jurisdiction
        and ("case" in authority_type or "opinion" in authority_type)
        and status not in EXCLUDED_PUBLIC_STATUSES
    )


def safe_public_source_url(value):
    value = str(value or "").strip()
    if not value:
        return None
    try:
        parsed = urlparse(value)
    except ValueError:
        return None
    return value if parsed.scheme == "https" and bool(parsed.netloc) else None


def public_case_payload(authority, *, include_text: bool = False):
    payload = {
        "id": authority.id,
        "title": authority.title,
        "citation": authority.citation,
        "court_or_type": authority.authority_type,
        "jurisdiction": authority.jurisdiction,
        "status": authority.status,
        "source_url": safe_public_source_url(authority.source_url),
        "effective_from": authority.effective_from,
        "effective_to": authority.effective_to,
        "retrieved_at": authority.retrieved_at,
    }
    if include_text:
        payload["text"] = authority.text
    else:
        payload["excerpt"] = " ".join(str(authority.text or "").split())[:700]
    return payload
