"""Search persisted Georgia legal authorities for grounded AI analysis."""
from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import LegalAuthority

_NEGATIVE = {"overruled", "vacated", "superseded", "withdrawn", "repealed"}
_VERIFIED = {"verified", "official", "validated", "confirmed"}
_STOP = {
    "about", "after", "also", "and", "are", "because", "been", "but", "can", "could",
    "does", "for", "from", "had", "has", "have", "how", "into", "not", "that", "the",
    "this", "was", "were", "what", "when", "who", "why", "with", "you", "your", "happens",
    "being", "will", "would", "should", "than", "then",
}
_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*")


@dataclass(frozen=True)
class AuthoritySearchResult:
    id: int
    citation: str
    title: str | None
    authority_type: str
    source_url: str | None
    status: str
    currency_status: str
    precedential_status: str
    text: str
    usable_as_support: bool


def search_terms(query: str, *, limit: int = 8) -> list[str]:
    """Keywords from a natural-language question. Does not invent citations."""
    terms: list[str] = []
    for token in _TOKEN.findall(query or ""):
        low = token.lower().strip(".-")
        if len(low) < 4 or low in _STOP or low in terms:
            continue
        terms.append(low)
        if len(terms) >= limit:
            break
    return terms


def _negative(authority: LegalAuthority) -> bool:
    values = {
        (authority.currency_status or "").lower(),
        (authority.precedential_status or "").lower(),
    }
    treatment = (authority.negative_treatment or "").lower()
    return bool(values & _NEGATIVE) or any(word in treatment for word in _NEGATIVE)


def _usable(authority: LegalAuthority) -> bool:
    return (
        (authority.status or "").lower() in _VERIFIED
        and not _negative(authority)
        and bool(authority.source_url and authority.source_url.startswith("https://"))
    )


def _term_filters(columns, terms: list[str]):
    clauses = []
    for term in terms:
        needle = f"%{term}%"
        clauses.extend(column.ilike(needle) for column in columns)
    return or_(*clauses)


def search_georgia_authorities(db: Session, query: str, *, limit: int = 8) -> list[AuthoritySearchResult]:
    terms = search_terms(query)
    if not terms:
        return []
    limit = max(1, min(limit, 25))
    columns = (LegalAuthority.citation, LegalAuthority.title, LegalAuthority.text)
    rows = (
        db.query(LegalAuthority)
        .filter(LegalAuthority.jurisdiction.ilike("%Georgia%"))
        .filter(_term_filters(columns, terms))
        .order_by(LegalAuthority.citation.asc())
        .limit(limit * 4)
        .all()
    )
    ranked = sorted(rows, key=lambda row: (_match_score(row, terms), row.citation or ""), reverse=True)
    return [
        AuthoritySearchResult(
            id=row.id,
            citation=row.citation,
            title=row.title,
            authority_type=row.authority_type,
            source_url=row.source_url,
            status=row.status,
            currency_status=row.currency_status or "unknown",
            precedential_status=row.precedential_status or "unknown",
            text=(row.text or "")[:12000],
            usable_as_support=_usable(row),
        )
        for row in ranked[:limit]
    ]


def _match_score(row: LegalAuthority, terms: list[str]) -> int:
    blob = " ".join([row.citation or "", row.title or "", row.text or ""]).lower()
    return sum(1 for term in terms if term in blob)


def persisted_authority_hits(db: Session, query: str, *, limit: int = 12) -> list[dict]:
    """Adapt persisted authorities to the same shape used by grounded retrieval.

    This is the bridge between the ingestion database and Case Analysis/Rights/
    Motions/Talk to Me.  Records remain visible for lookup, but only records
    passing ``usable_as_support`` can become grounded legal support.
    A keyword miss is an empty list, not a fabricated authority.
    """
    hits = []
    for row in search_georgia_authorities(db, query, limit=limit):
        hits.append({
            "corpus": "persisted_authorities",
            "score": 2.0 if row.usable_as_support else 1.0,
            "title": row.title or row.citation,
            "citation": row.citation,
            "source_url": row.source_url,
            "verification_status": row.status,
            "excerpt": row.text[:900],
            "record_type": row.authority_type,
            "court": None,
            "case_number": None,
            "docket_number": None,
            "decision_date": None,
            "section_number": None,
            "effective_date": None,
            "jurisdiction": "Georgia",
            "currency_status": row.currency_status,
            "precedential_status": row.precedential_status,
            "status_checked_at": None,
            "status_source_url": None,
            "superseded_by": None,
            "negative_treatment": [],
            "usable_as_support": row.usable_as_support,
            "authority_id": row.id,
        })
    return hits
