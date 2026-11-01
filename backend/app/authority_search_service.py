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


# --- Fast path: stored weighted search_vector (migration 20261101) ---------------------------
# search_vector = citation+title (A) || first 600 chars of text (B) || rest of text (C), GIN indexed.
SEARCH_VECTOR_INDEX = "ix_legal_authorities_search_vector"
_RANK_WEIGHTS = "{0.05, 0.2, 0.5, 1.0}"  # D, C, B, A
_STRICT_CANDIDATES = 1500   # bound ranking work on very common words (opinions)
_LOOSE_CANDIDATES = 600
_TYPE_BOOST = {"statute": 1.6, "court_rule": 1.3, "regulation": 1.0}
_SV_STATE: dict = {"checked_at": 0.0, "ready": False}
_SV_TTL_SECONDS = 300.0

# Plain-English -> Georgia legal vocabulary. Each entry: trigger words/phrases found in the
# question, extra search terms (OR'd in), and O.C.G.A. sections to look up by exact citation.
# Pinned sections are only shown when that exact citation exists in the database (nothing is
# invented); they are retrieval hints, not legal text.
QUERY_EXPANSIONS: tuple[tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]], ...] = (
    (("evict", "eviction", "evicted", "kicked out", "dispossessory"),
     ("dispossessory", "landlord", "tenant", "notice to quit", "possession"),
     ("44-7-50", "44-7-51", "44-7-7")),
    (("landlord", "tenant", "renter", "lease"), ("landlord", "tenant", "rent"), ()),
    (("security deposit", "deposit back"), ("security deposit",), ("44-7-34", "44-7-35")),
    (("landlord won't fix", "landlord will not fix", "mold", "habitab", "uninhabitable"), ("landlord", "repairs"), ("44-7-13",)),
    (("divorce", "divorced", "dissolution"), ("divorce", "alimony"), ("19-5-1", "19-5-2", "19-5-3", "19-5-5")),
    (("custody", "visitation", "parenting time"), ("custody", "visitation"), ("19-9-3",)),
    (("child support",), ("child support",), ("19-6-15",)),
    (("dui", "drunk driving", "driving drunk", "under the influence", "dwi"),
     ("influence", "alcohol", "intoxicated"), ("40-6-391",)),
    (("suspended license", "driving on suspended", "revoked license"), ("suspended", "license"), ("40-5-121",)),
    (("shoplift", "shoplifting", "stealing", "stole", "theft"), ("theft",), ("16-8-2", "16-8-14", "16-8-12")),
    (("assault",), ("assault",), ("16-5-20", "16-5-21")),
    (("battery", "hit someone", "punched"), ("battery",), ("16-5-23", "16-5-23.1")),
    (("domestic violence", "family violence", "protective order", "restraining order"),
     ("family violence", "protective order"), ("19-13-1", "19-13-3", "19-13-4")),
    (("trespass", "trespassing"), ("criminal trespass",), ("16-7-21",)),
    (("disorderly",), ("disorderly conduct",), ("16-11-39",)),
    (("obstruction", "resisting arrest", "resist arrest"), ("obstruction", "officer"), ("16-10-24",)),
    (("gun", "firearm", "weapon", "pistol", "carry license", "concealed carry"), ("weapon", "firearm", "carry"), ("16-11-126", "16-11-127", "16-11-129")),
    (("marijuana", "weed", "cannabis", "drugs", "possession of", "cocaine", "meth"),
     ("controlled substance", "marijuana", "possession"), ("16-13-30", "16-13-2")),
    (("pulled over", "traffic stop", "search my car", "search the car", "search warrant", "searched"),
     ("search", "warrant", "seizure"), ("17-5-1", "17-5-21", "17-5-30")),
    (("first offender",), ("first offender",), ("42-8-60",)),
    (("expunge", "expungement", "record restriction", "clear my record"), ("restriction", "record"), ("35-3-37",)),
    (("self defense", "self-defense", "defend myself", "stand your ground"), ("justification", "force"), ("16-3-21", "16-3-23.1")),
    (("workers comp", "workers' comp", "hurt at work", "injured at work"), ("workers compensation",), ("34-9-1",)),
    (("statute of limitations", "too late to sue", "personal injury"), ("limitation",), ("9-3-33",)),
    (("speeding",), ("speed",), ("40-6-181",)),
)
_SECTION_IN_QUERY = re.compile(r"\b(\d{1,2}[A-Z]?-\d{1,3}[A-Z]?-\d{1,4}(?:\.\d+)?)\b")


@dataclass(frozen=True)
class QueryPlan:
    keywords: tuple[str, ...]
    expansion_terms: tuple[str, ...]
    pinned_citations: tuple[str, ...]


def build_query_plan(query: str) -> QueryPlan:
    """Keywords + plain-English expansions + exact citations to pin for a user question."""
    lowered = f" {(query or '').lower()} "
    keywords = search_keywords(query)
    extra: dict[str, None] = {}
    pinned: dict[str, None] = {}
    for section in _SECTION_IN_QUERY.findall(query or ""):
        pinned[f"O.C.G.A. § {section}"] = None
    for triggers, terms, sections in QUERY_EXPANSIONS:
        if any(re.search(rf"\b{re.escape(t)}", lowered) for t in triggers):
            for term in terms:
                if term not in keywords:
                    extra[term] = None
            for section in sections:
                pinned[f"O.C.G.A. § {section}"] = None
    return QueryPlan(tuple(keywords), tuple(extra), tuple(pinned))


def max_pinned(limit: int) -> int:
    """Pinned exact citations never take more than about half the result slots."""
    return max(3, (limit + 1) // 2)


def _websearch_text(words, joiner: str) -> str:
    parts = []
    for w in words:
        w = w.replace('"', " ").strip()
        if not w:
            continue
        parts.append(f'"{w}"' if " " in w else w)
    return joiner.join(parts)


def search_vector_ready(db: Session) -> bool:
    """True once the search_vector GIN index exists and is valid (backfill finished)."""
    import time
    now = time.monotonic()
    if now - _SV_STATE["checked_at"] < _SV_TTL_SECONDS:
        return _SV_STATE["ready"]
    from sqlalchemy import text as sql_text
    try:
        with db.begin_nested():
            ready = bool(db.execute(sql_text(
                "SELECT EXISTS (SELECT 1 FROM pg_index WHERE indexrelid = to_regclass(:name) AND indisvalid)"
            ), {"name": f"public.{SEARCH_VECTOR_INDEX}"}).scalar())
    except Exception:
        ready = False
    _SV_STATE.update(checked_at=now, ready=ready)
    return ready


def _pinned_rows(db: Session, citations, filters: tuple) -> list[LegalAuthority]:
    if not citations:
        return []
    rows = (
        db.query(LegalAuthority)
        .filter(LegalAuthority.citation.in_(list(citations)))
        .filter(LegalAuthority.jurisdiction.ilike("Georgia"))
        .filter(*filters)
        .all()
    )
    order = {c: i for i, c in enumerate(citations)}
    rows.sort(key=lambda r: order.get(r.citation, 999))
    seen, out = set(), []
    for row in rows:
        if row.citation not in seen:
            seen.add(row.citation)
            out.append(row)
    return out


def _vector_rows(db: Session, term: str, plan: QueryPlan, limit: int, filters: tuple) -> list[LegalAuthority]:
    from sqlalchemy import Float, select
    from sqlalchemy import cast as sa_cast
    cfg = literal_column(f"'{FTS_CONFIG}'::regconfig")
    sv = literal_column("legal_authorities.search_vector")
    weights = literal_column(f"'{_RANK_WEIGHTS}'::float4[]")
    words = list(plan.keywords)
    strict_text = _websearch_text(words, " ")
    loose_text = _websearch_text(words + list(plan.expansion_terms), " or ")
    loose_q = func.websearch_to_tsquery(cfg, loose_text)
    strict_q = func.websearch_to_tsquery(cfg, strict_text)
    if plan.expansion_terms:
        # The user's words all present, OR any of the legal-vocabulary expansions.
        strict_q = strict_q.op("||")(func.websearch_to_tsquery(cfg, _websearch_text(plan.expansion_terms, " or ")))
    type_boost = case(
        *[(func.lower(LegalAuthority.authority_type) == k, v) for k, v in _TYPE_BOOST.items()], else_=0.8
    )

    found: list[LegalAuthority] = []
    found.extend(_pinned_rows(db, plan.pinned_citations, filters)[:max_pinned(limit)])
    if re.search(r"\d", term) and len(term) <= 60:
        cites = (
            db.query(LegalAuthority).filter(LegalAuthority.citation.ilike(f"%{term}%"))
            .filter(LegalAuthority.jurisdiction.ilike("Georgia")).filter(*filters)
            .order_by(func.length(LegalAuthority.citation), LegalAuthority.citation).limit(limit).all()
        )
        found.extend(r for r in cites if r.id not in {f.id for f in found})

    stages = [(strict_q, _STRICT_CANDIDATES)] if words or plan.expansion_terms else []
    if words and (len(words) > 1 or plan.expansion_terms):
        stages.append((loose_q, _LOOSE_CANDIDATES))
    for tsq, cap in stages:
        if len(found) >= limit:
            break
        exclude = [f.id for f in found]
        candidates = (
            select(LegalAuthority.id.label("cid"))
            .where(sv.op("@@")(tsq))
            .where(LegalAuthority.jurisdiction.ilike("Georgia"))
            .where(*filters)
        )
        if exclude:
            candidates = candidates.where(LegalAuthority.id.notin_(exclude))
        candidates = candidates.limit(cap).subquery()
        rank = func.ts_rank_cd(weights, sv, loose_q, 1) * sa_cast(type_boost, Float)
        rows = (
            db.query(LegalAuthority)
            .join(candidates, candidates.c.cid == LegalAuthority.id)
            .order_by(rank.desc(), LegalAuthority.citation.asc())
            .limit(limit - len(found))
            .all()
        )
        found.extend(rows)
    return found[:limit]


def _postgres_rows(db: Session, term: str, keywords: list[str], limit: int, filters: tuple = ()) -> list[LegalAuthority]:
    if search_vector_ready(db):
        return _vector_rows(db, term, build_query_plan(term), limit, filters)
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
        .filter(*filters)
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


def _fallback_rows(db: Session, term: str, keywords: list[str], limit: int, filters: tuple = ()) -> list[LegalAuthority]:
    """Portable word-based search (SQLite tests / non-Postgres databases)."""
    clauses = [LegalAuthority.citation.ilike(f"%{term}%")]
    for word in keywords:
        like = f"%{word}%"
        clauses.extend([LegalAuthority.citation.ilike(like), LegalAuthority.title.ilike(like), LegalAuthority.text.ilike(like)])
    candidates = (
        db.query(LegalAuthority)
        .filter(LegalAuthority.jurisdiction.ilike("Georgia"))
        .filter(or_(*clauses))
        .filter(*filters)
        .limit(_SQLITE_CANDIDATES)
        .all()
    )
    pinned = _pinned_rows(db, build_query_plan(term).pinned_citations, filters)[:max_pinned(limit)]
    pinned_ids = {row.id for row in pinned}
    scored = [(row, _fallback_score(row, term, keywords)) for row in candidates if row.id not in pinned_ids]
    scored = [item for item in scored if item[1] > 0]
    scored.sort(key=lambda item: (-item[1], item[0].citation or ""))
    return (pinned + [row for row, _ in scored])[:limit]


def search_georgia_authorities(db: Session, query: str, *, limit: int = 8, filters: tuple = ()) -> list[AuthoritySearchResult]:
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
        rows = _postgres_rows(db, term, keywords, limit, filters)
    else:
        rows = _fallback_rows(db, term, keywords, limit, filters)
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


_PRIMARY_TYPES = ("statute", "court_rule", "regulation")


def _to_result(row: LegalAuthority) -> AuthoritySearchResult:
    return AuthoritySearchResult(
        id=row.id, citation=row.citation, title=row.title, authority_type=row.authority_type,
        source_url=row.source_url, status=row.status, currency_status=row.currency_status or "unknown",
        precedential_status=row.precedential_status or "unknown", text=(row.text or "")[:12000],
        usable_as_support=_usable(row),
    )


def exact_citation_results(db: Session, citations) -> list[AuthoritySearchResult]:
    """Exact-citation lookup (btree on citation). Citations not in the database are dropped."""
    cites = [c for c in dict.fromkeys(citations or []) if c]
    return [_to_result(row) for row in _pinned_rows(db, cites, ())] if cites else []


def grounding_search(db: Session, query: str, *, limit: int = 12) -> list[AuthoritySearchResult]:
    """AI grounding: statutes / court rules / regulations first, then case law, de-duplicated."""
    limit = max(1, min(limit, 25))
    primary_n = max(1, (limit * 2 + 2) // 3)
    primary = search_georgia_authorities(
        db, query, limit=primary_n, filters=(func.lower(LegalAuthority.authority_type).in_(_PRIMARY_TYPES),))
    cases = search_georgia_authorities(
        db, query, limit=limit - len(primary) if len(primary) < limit else 0,
        filters=(func.lower(LegalAuthority.authority_type).notin_(_PRIMARY_TYPES),)) if len(primary) < limit else []
    seen, out = set(), []
    for row in primary + cases:
        if row.id not in seen:
            seen.add(row.id); out.append(row)
    return out[:limit]


def authority_hit(row: AuthoritySearchResult) -> dict:
    return {
        "corpus": "persisted_authorities",
        "score": 2.0 if row.usable_as_support else 1.0,
        "title": row.title or row.citation,
        "citation": row.citation,
        "source_url": row.source_url,
        "verification_status": row.status,
        "excerpt": row.text[:900],
        "record_type": row.authority_type,
        "court": None, "case_number": None, "docket_number": None, "decision_date": None,
        "section_number": None, "effective_date": None,
        "jurisdiction": "Georgia",
        "currency_status": row.currency_status,
        "precedential_status": row.precedential_status,
        "status_checked_at": None, "status_source_url": None, "superseded_by": None,
        "negative_treatment": [],
        "usable_as_support": row.usable_as_support,
        "authority_id": row.id,
    }


def persisted_authority_hits(db: Session, query: str, *, limit: int = 12, extra_citations=()) -> list[dict]:
    """Adapt persisted authorities to the same shape used by grounded retrieval.

    This is the bridge between the ingestion database and Case Analysis/Rights/
    Motions/Talk to Me.  Records remain visible for lookup, but only records
    passing ``usable_as_support`` can become grounded legal support.
    ``extra_citations`` (e.g. model-proposed O.C.G.A. sections) are looked up by exact
    citation and merged in; any that are not in the database are dropped.
    """
    rows = grounding_search(db, query, limit=limit)
    extra = exact_citation_results(db, extra_citations) if extra_citations else []
    if extra:
        have = {r.id for r in rows}
        extra = [r for r in extra if r.id not in have]
        keep = max(0, limit - min(len(extra), max(1, limit // 3)))
        primary = [r for r in rows if (r.authority_type or "").lower() in _PRIMARY_TYPES]
        others = [r for r in rows if (r.authority_type or "").lower() not in _PRIMARY_TYPES]
        rows = (primary + extra + others)[:max(limit, keep)]
    return [authority_hit(row) for row in rows[:limit]]


# Georgia Laws screen tabs -> persisted authority types.
PUBLIC_LAW_KINDS = {
    "statutes": ("statute", "regulation"),
    "case_law": ("case_law", "case", "opinion"),
    "court_rules": ("court_rule",),
}
_PUBLIC_EXCLUDED_STATUSES = ("sealed", "juvenile", "expunged", "restricted", "private", "unavailable")
_SECTION_PART = re.compile(r"^[0-9]{1,3}[A-Za-z]?$")


def public_law_search(db: Session, *, kind: str, keyword: str = "", title: str = "", chapter: str = "", limit: int = 25) -> list[AuthoritySearchResult]:
    """Guest Georgia Laws search over persisted public authorities (no private user data).

    ``title``/``chapter`` narrow O.C.G.A. statutes by citation prefix (e.g. 16 / 11 ->
    "O.C.G.A. § 16-11-"). With no keyword, statutes in that title/chapter are listed in
    citation order. Restricted records are never returned.
    """
    types = PUBLIC_LAW_KINDS.get(kind)
    if types is None:
        raise ValueError("Unsupported law kind.")
    limit = max(1, min(int(limit), 25))
    filters = [
        func.lower(LegalAuthority.authority_type).in_(types),
        func.lower(func.coalesce(LegalAuthority.status, "")).notin_(_PUBLIC_EXCLUDED_STATUSES),
    ]
    title = (title or "").strip(); chapter = (chapter or "").strip()
    if title:
        if not _SECTION_PART.match(title) or (chapter and not _SECTION_PART.match(chapter)):
            raise ValueError("Title and chapter must be numbers such as 16 and 11.")
        prefix = f"O.C.G.A. § {title}-" + (f"{chapter}-" if chapter else "")
        filters.append(LegalAuthority.citation.ilike(prefix + "%"))
    filters = tuple(filters)
    term = (keyword or "").strip()
    if term:
        return search_georgia_authorities(db, term, limit=limit, filters=filters)
    if not title:
        return []
    rows = (
        db.query(LegalAuthority)
        .filter(LegalAuthority.jurisdiction.ilike("Georgia"))
        .filter(*filters)
        .order_by(LegalAuthority.citation.asc())
        .limit(limit)
        .all()
    )
    return [
        AuthoritySearchResult(id=row.id, citation=row.citation, title=row.title, authority_type=row.authority_type,
                              source_url=row.source_url, status=row.status, currency_status=row.currency_status or "unknown",
                              precedential_status=row.precedential_status or "unknown", text=(row.text or "")[:12000],
                              usable_as_support=_usable(row))
        for row in rows
    ]
