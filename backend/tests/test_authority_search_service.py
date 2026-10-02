from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import LegalAuthority
from app.authority_search_service import search_georgia_authorities


def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def add(db, citation, text, *, status="OFFICIAL", currency="current", precedent="unknown", negative=None):
    db.add(LegalAuthority(
        jurisdiction="Georgia", authority_type="case_law", citation=citation,
        title="Georgia authority", text=text, status=status,
        source_url="https://www.gasupreme.us/example", retrieved_at=datetime.utcnow(),
        currency_status=currency, precedential_status=precedent,
        negative_treatment=negative,
    ))
    db.commit()


def test_search_returns_matching_persisted_authority():
    db = session(); add(db, "S26A1234", "search and seizure probable cause")
    result = search_georgia_authorities(db, "probable cause")
    assert len(result) == 1
    assert result[0].citation == "S26A1234"
    assert result[0].usable_as_support is True


def test_negative_treatment_is_searchable_but_never_marked_usable_support():
    db = session(); add(db, "S20A0001", "suppression", currency="vacated", negative="vacated")
    result = search_georgia_authorities(db, "suppression")
    assert len(result) == 1
    assert result[0].usable_as_support is False


def test_unverified_authority_is_not_marked_usable_support():
    db = session(); add(db, "A26A9999", "identification evidence", status="UNVERIFIED")
    result = search_georgia_authorities(db, "identification")
    assert result[0].usable_as_support is False


def test_blank_query_returns_nothing_and_limit_is_bounded():
    db = session()
    assert search_georgia_authorities(db, "   ") == []

def test_natural_question_matches_shared_legal_terms_not_the_whole_phrase():
    db = session()
    add(db, "S25A0101", "The opinion discusses murder and malice aforethought.")
    add(db, "S25A0102", "This opinion discusses a traffic citation only.")
    result = search_georgia_authorities(db, "what happens if you are charged for murder")
    assert [row.citation for row in result] == ["S25A0101"]


def test_unrelated_question_does_not_invent_a_hit():
    db = session(); add(db, "S25A0101", "The opinion discusses murder and malice aforethought.")
    assert search_georgia_authorities(db, "what is the filing fee for a name change") == []

