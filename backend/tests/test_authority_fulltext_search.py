"""Issue #88 item 4: natural questions must find persisted authorities by words, not by
matching the whole question as one ILIKE substring."""
import os
from datetime import datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.authority_search_service import search_georgia_authorities, search_keywords
from app.database import Base
from app.models import LegalAuthority

POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")


def _sqlite():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _seed(db):
    rows = [
        ("Georgia", "O.C.G.A. § 16-5-1", "Murder; felony murder", "A person commits the offense of murder when he unlawfully and with malice aforethought causes the death of another human being. Punishment for murder is death, life imprisonment without parole, or life imprisonment."),
        ("Georgia", "S26A0101", "Smith v. State", "Appeal from a conviction for felony murder and aggravated assault; sufficiency of the evidence."),
        ("Georgia", "O.C.G.A. § 40-6-391", "Driving under the influence", "A person shall not drive or be in actual physical control of any moving vehicle while under the influence of alcohol."),
        ("Florida", "Fla. Stat. 782.04", "Murder", "Florida murder statute."),
    ]
    for jurisdiction, citation, title, body in rows:
        db.add(LegalAuthority(
            jurisdiction=jurisdiction, authority_type="statute", citation=citation, title=title, text=body,
            status="OFFICIAL", source_url="https://law.example.gov/" + citation.replace(" ", ""),
            retrieved_at=datetime.utcnow(), currency_status="unknown", precedential_status="unknown",
        ))
    db.commit()


def test_keywords_drop_stop_words_and_keep_citations():
    assert search_keywords("What happens if you are charged for murder in Georgia?") == ["murder"]
    assert search_keywords("O.C.G.A. § 16-5-1 punishment") == ["o.c.g.a", "16-5-1", "punishment"]
    many = search_keywords(" ".join(f"word{i}" for i in range(100)))
    assert many == [f"word{i}" for i in range(76, 100)]  # most recent words win
    prompt = "Continue a focused conversation about rights, police, motions, sentencing, appeals. " * 3 + "User: what is the punishment for murder"
    assert search_keywords(prompt)[-2:] == ["punishment", "murder"]


def _check_search_behaviour(db):
    hits = search_georgia_authorities(db, "what happens if you are charged for murder")
    citations = [h.citation for h in hits]
    assert "O.C.G.A. § 16-5-1" in citations and "S26A0101" in citations
    assert "Fla. Stat. 782.04" not in citations  # Georgia only
    assert "O.C.G.A. § 40-6-391" not in citations

    ranked = search_georgia_authorities(db, "murder punishment life imprisonment")
    assert ranked[0].citation == "O.C.G.A. § 16-5-1"

    dui = search_georgia_authorities(db, "Can I be arrested for driving under the influence of alcohol?")
    assert dui[0].citation == "O.C.G.A. § 40-6-391"

    by_citation = search_georgia_authorities(db, "S26A0101")
    assert by_citation[0].citation == "S26A0101"

    assert search_georgia_authorities(db, "zoning variance easement") == []
    assert len(search_georgia_authorities(db, "murder", limit=1)) == 1


def test_word_based_search_on_sqlite_fallback():
    db = _sqlite()
    _seed(db)
    _check_search_behaviour(db)


@pytest.mark.skipif(not POSTGRES_URL, reason="set TEST_POSTGRES_URL to run against PostgreSQL full-text search")
def test_postgres_full_text_search_uses_ranked_tsquery_and_gin_index():
    engine = create_engine(POSTGRES_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        db = sessionmaker(bind=engine)()
        _seed(db)
        _check_search_behaviour(db)
        indexes = db.execute(text("select indexdef from pg_indexes where indexname = 'ix_legal_authorities_fulltext'")).scalars().all()
        assert indexes and "gin" in indexes[0].lower() and "to_tsvector" in indexes[0]
        db.execute(text("set enable_seqscan = off"))
        from app.authority_search_service import authority_document_expression
        from sqlalchemy import func, literal_column, select
        stmt = select(LegalAuthority.id).where(
            authority_document_expression().op("@@")(func.websearch_to_tsquery(literal_column("'english'::regconfig"), "murder"))
        )
        compiled = stmt.compile(engine, compile_kwargs={"literal_binds": True})
        plan = "\n".join(db.execute(text(f"EXPLAIN {compiled}")).scalars().all())
        assert "ix_legal_authorities_fulltext" in plan
        db.close()
    finally:
        Base.metadata.drop_all(engine)
