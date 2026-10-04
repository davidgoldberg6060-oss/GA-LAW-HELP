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


def _unknown_if_blank(value):
    text = str(value or "").strip()
    return text or "unknown"


def public_case_payload(authority, *, include_text: bool = False):
    payload = {
        "id": authority.id,
        "title": authority.title,
        "citation": authority.citation,
        "court_or_type": authority.authority_type,
        "jurisdiction": authority.jurisdiction,
        "status": authority.status,
        "currency_status": _unknown_if_blank(getattr(authority, "currency_status", None)),
        "precedential_status": _unknown_if_blank(getattr(authority, "precedential_status", None)),
        "status_checked_at": getattr(authority, "status_checked_at", None),
        "status_source_url": safe_public_source_url(getattr(authority, "status_source_url", None)),
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


def _safe_like_token(value: str) -> str:
    return str(value or "").replace("%", "").replace("_", "").strip()


def public_case_keyword_clause(query_text: str):
    """Match indexed public cases by keywords, not the entire natural-language question.

    A whole-question ILIKE misses opinions that contain only some of the words.
    A hit is an index match only. It is not a claim that the citation is current Georgia law.
    Private user cases are never part of this clause.
    """
    from sqlalchemy import or_

    from .authority_search_service import search_keywords
    from .models import LegalAuthority

    term = (query_text or "").strip()
    if not term:
        return None
    keywords = search_keywords(term)
    needles = keywords or [_safe_like_token(term[:80])]
    clauses = []
    for word in needles[:12]:
        token = _safe_like_token(word)
        if len(token) < 2:
            continue
        like = f"%{token}%"
        clauses.extend(
            [
                LegalAuthority.citation.ilike(like),
                LegalAuthority.title.ilike(like),
                LegalAuthority.text.ilike(like),
            ]
        )
    if not clauses:
        return None
    return or_(*clauses)
