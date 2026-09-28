"""Search persisted Georgia legal authorities for grounded AI analysis."""
from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import LegalAuthority

_NEGATIVE = {"overruled", "vacated", "superseded", "withdrawn", "repealed"}
_VERIFIED = {"verified", "official", "validated", "confirmed"}


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


def search_georgia_authorities(db: Session, query: str, *, limit: int = 8) -> list[AuthoritySearchResult]:
    term = (query or "").strip()
    if not term:
        return []
    limit = max(1, min(limit, 25))
    needle = f"%{term}%"
    rows = (
        db.query(LegalAuthority)
        .filter(LegalAuthority.jurisdiction.ilike("Georgia"))
        .filter(
            or_(
                LegalAuthority.citation.ilike(needle),
                LegalAuthority.title.ilike(needle),
                LegalAuthority.text.ilike(needle),
            )
        )
        .order_by(LegalAuthority.citation.asc())
        .limit(limit)
        .all()
    )
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
        for row in rows
    ]
