"""Search persisted Georgia legal authorities for grounded AI analysis."""
from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import case, func, literal_column, or_
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


_STOPWORDS = frozenset(
    """a about after again against all am an and any are as at be because been before being between both
    but by can could did do does doing during each few for from further had has have having he her here
    hers him his how i if in into is it its itself just me more most my no nor not now of off on once only
    or other our out over own same she should so some such than that the their them then there these they
    this those through to too under until up very was we were what when where which while who whom why
    will with would you your yours georgia ga law laws legal question questions please tell know want
    happens happen get got charged""".split()
)
_TOKEN = re.compile(r"[a-z0-9]+(?:[-.:][a-z0-9]+)*")
MAX_KEYWORDS = 24
_SQLITE_CANDIDATES = 500

# Must stay identical to the GIN expression index in
# backend/migrations/20261004_authority_fulltext_search.sql and the model Index.
FTS_CONFIG = "english"


def search_keywords(query: str) -> list[str]:
    """Distinct keywords from a natural-language question (stop words removed).

    When there are more than MAX_KEYWORDS, the most recent ones are kept: conversational
    prompts (Talk to Me) put instructions and history first and the user's message last.
    """
    seen: dict[str, None] = {}
    for token in _TOKEN.findall((query or "").lower()):
        token = token.strip(".-:")
        if len(token) < 2 or token in _STOPWORDS:
            continue
        seen.pop(token, None)
        seen[token] = None
    return list(seen)[-MAX_KEYWORDS:]


def fts_document_text():
    """citation || ' ' || title || ' ' || text using only IMMUTABLE operators (indexable)."""
    return (
        func.coalesce(LegalAuthority.citation, "") + " "
        + func.coalesce(LegalAuthority.title, "") + " "
        + func.coalesce(LegalAuthority.text, "")
    )


def authority_document_expression():
    """tsvector over citation + title + text (Postgres only)."""
    return func.to_tsvector(literal_column(f"'{FTS_CONFIG}'::regconfig"), fts_document_text())


def _postgres_rows(db: Session, term: str, keywords: list[str], limit: int) -> list[LegalAuthority]:
    needle = f"%{term}%"
    citation_hit = LegalAuthority.citation.ilike(needle)
    if keywords:
        document = authority_document_expression()
        # OR semantics so a long natural question still matches; ranking rewards coverage.
        tsquery = func.websearch_to_tsquery(literal_column(f"'{FTS_CONFIG}'::regconfig"), " or ".join(keywords))
        rank = func.ts_rank_cd(document, tsquery) + case((citation_hit, 1.0), else_=0.0)
        match = or_(document.op("@@")(tsquery), citation_hit)
    else:
        rank = case((citation_hit, 1.0), else_=0.0)
        match = citation_hit
    return (
        db.query(LegalAuthority)
        .filter(LegalAuthority.jurisdiction.ilike("Georgia"))
        .filter(match)
        .order_by(rank.desc(), LegalAuthority.citation.asc())
        .limit(limit)
        .all()
    )


def _fallback_score(row: LegalAuthority, term: str, keywords: list[str]) -> float:
    citation = (row.citation or "").lower()
    title = (row.title or "").lower()
    text = (row.text or "").lower()
    score = 10.0 if term.lower() in citation else 0.0
    for word in keywords:
        if word in citation:
            score += 3.0
        if word in title:
            score += 2.0
        occurrences = text.count(word)
        if occurrences:
            score += 1.0 + min(occurrences, 10) * 0.05
    return score


def _fallback_rows(db: Session, term: str, keywords: list[str], limit: int) -> list[LegalAuthority]:
    """Portable word-based search (SQLite tests / non-Postgres databases)."""
    clauses = [LegalAuthority.citation.ilike(f"%{term}%")]
    for word in keywords:
        like = f"%{word}%"
        clauses.extend([LegalAuthority.citation.ilike(like), LegalAuthority.title.ilike(like), LegalAuthority.text.ilike(like)])
    candidates = (
        db.query(LegalAuthority)
        .filter(LegalAuthority.jurisdiction.ilike("Georgia"))
        .filter(or_(*clauses))
        .limit(_SQLITE_CANDIDATES)
        .all()
    )
    scored = [(row, _fallback_score(row, term, keywords)) for row in candidates]
    scored = [item for item in scored if item[1] > 0]
    scored.sort(key=lambda item: (-item[1], item[0].citation or ""))
    return [row for row, _ in scored[:limit]]


def search_georgia_authorities(db: Session, query: str, *, limit: int = 8) -> list[AuthoritySearchResult]:
    """Word-based search of persisted Georgia authorities, best matches first.

    Postgres uses full-text search (to_tsvector / websearch_to_tsquery, ranked with ts_rank_cd,
    backed by a GIN expression index). Other databases use a word-based ILIKE fallback with the
    same keywords. A citation containing the whole query is always matched and ranked first.
    """
    term = (query or "").strip()
    if not term:
        return []
    limit = max(1, min(limit, 25))
    keywords = search_keywords(term)
    bind = db.get_bind()
    if bind is not None and bind.dialect.name == "postgresql":
        rows = _postgres_rows(db, term, keywords, limit)
    else:
        rows = _fallback_rows(db, term, keywords, limit)
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


def persisted_authority_hits(db: Session, query: str, *, limit: int = 12) -> list[dict]:
    """Adapt persisted authorities to the same shape used by grounded retrieval.

    This is the bridge between the ingestion database and Case Analysis/Rights/
    Motions/Talk to Me.  Records remain visible for lookup, but only records
    passing ``usable_as_support`` can become grounded legal support.
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
