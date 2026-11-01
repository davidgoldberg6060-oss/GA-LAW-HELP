"""Query builder, plain-English expansion, pinned exact citations and AI citation proposals."""
from datetime import datetime

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app import citation_proposer, grounded_legal_assistant as gla
from app.authority_search_service import (
    _websearch_text, build_query_plan, max_pinned, public_law_search, search_georgia_authorities,
)
from app.database import Base
from app.models import LegalAuthority


def _db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    rows = [
        ("statute", "O.C.G.A. § 44-7-50", "Demand for possession; dispossessory affidavit", "In all cases when a tenant holds possession of lands after the term..."),
        ("statute", "O.C.G.A. § 44-7-7", "Tenancy at will; notice to terminate", "Two months' notice by the landlord or one month's notice by the tenant..."),
        ("statute", "O.C.G.A. § 19-8-26", "Adoption forms", "Notice of rights to the tenant of a surrender form; rights notice."),
        ("statute", "O.C.G.A. § 19-5-3", "Grounds for divorce", "The grounds for total divorce shall be ..."),
        ("opinion", "Smith v. Jones, 300 Ga. 1", "Smith v. Jones", "Landlord tenant dispossessory eviction notice appeal."),
    ]
    for kind, cite, title, body in rows:
        db.add(LegalAuthority(jurisdiction="Georgia", authority_type=kind, citation=cite, title=title, text=body,
                              status="OFFICIAL", source_url="https://law.example.gov/x", retrieved_at=datetime.utcnow(),
                              currency_status="unknown", precedential_status="unknown"))
    db.commit()
    return db


def test_query_plan_expands_plain_english_and_pins_sections():
    plan = build_query_plan("tenant rights eviction notice")
    assert "dispossessory" in plan.expansion_terms and "\"notice to quit\"" in plan.expansion_terms
    assert plan.pinned_citations[:2] == ("O.C.G.A. § 44-7-50", "O.C.G.A. § 44-7-51")
    assert "O.C.G.A. § 19-5-3" in build_query_plan("how to file for divorce in Georgia").pinned_citations
    assert "O.C.G.A. § 40-6-391" in build_query_plan("first DUI").pinned_citations
    assert build_query_plan("what does 16-5-1 say").pinned_citations[0] == "O.C.G.A. § 16-5-1"
    assert build_query_plan("current events").pinned_citations == ()  # 'rent' trigger must not fire
    assert build_query_plan("zoning variance").expansion_terms == ()
    assert _websearch_text(["tenant", "notice to quit", 'a"b'], " or ") == 'tenant or "notice to quit" or "a b"'
    assert max_pinned(25) == 13 and max_pinned(4) == 3


def test_eviction_query_ranks_dispossessory_statutes_first():
    db = _db()
    rows = public_law_search(db, kind="statutes", keyword="tenant rights eviction notice")
    assert [r.citation for r in rows[:2]] == ["O.C.G.A. § 44-7-50", "O.C.G.A. § 44-7-7"]
    assert rows[0].usable_as_support


def test_pinned_statutes_respect_type_filters_for_case_search():
    db = _db()
    rows = search_georgia_authorities(db, "tenant rights eviction notice",
                                      filters=(func.lower(LegalAuthority.authority_type) == "opinion",))
    assert [r.citation for r in rows] == ["Smith v. Jones, 300 Ga. 1"]


def test_parse_sections_keeps_only_section_numbers():
    raw = '{"sections":["O.C.G.A. § 17-5-1","40-6-391","bogus","17-5-1","16-13-30.1"]}'
    assert citation_proposer.parse_sections(raw) == ["17-5-1", "40-6-391", "16-13-30.1"]
    assert citation_proposer.parse_sections("not json") == []


def test_hybrid_retrieval_merges_proposed_sections_and_drops_missing(monkeypatch):
    db = _db()
    monkeypatch.setattr(citation_proposer, "enabled", lambda: True)
    monkeypatch.setattr(citation_proposer, "propose", lambda q: (["19-5-3", "99-99-99"], ""))
    result = gla._hybrid_retrieval("my landlord gave me an eviction notice", "rights", db=db, limit=6)
    cites = [h["citation"] for h in result["hits"] if h.get("corpus") == "persisted_authorities"]
    assert "O.C.G.A. § 19-5-3" in cites and "O.C.G.A. § 99-99-99" not in cites
    assert cites[0] == "O.C.G.A. § 44-7-50"


def test_proposer_disabled_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert citation_proposer.enabled() is False
    assert citation_proposer.propose_sections("anything") == []
