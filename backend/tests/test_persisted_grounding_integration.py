from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import LegalAuthority
from app import grounded_legal_assistant as service


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _add(db, *, citation, text, status="OFFICIAL", currency="current", precedent="unknown", negative=None):
    db.add(LegalAuthority(
        jurisdiction="Georgia",
        authority_type="case_law",
        citation=citation,
        title="Persisted Georgia opinion",
        text=text,
        status=status,
        source_url="https://www.gasupreme.us/opinion/example",
        retrieved_at=datetime.utcnow(),
        currency_status=currency,
        precedential_status=precedent,
        negative_treatment=negative,
    ))
    db.commit()


def _empty_file_corpus(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: {
        "hits": [], "coverage_notice": "Indexed file corpus returned no match."
    })


def test_persisted_verified_authority_reaches_all_grounded_ai_modes(monkeypatch):
    db = _session()
    _add(db, citation="321 Ga. 654", text="distinctive persisted search and seizure phrase")
    _empty_file_corpus(monkeypatch)

    for mode in ("case_analysis", "rights", "motions", "talk_to_me"):
        prompts = []
        result = service.grounded_legal_response(
            "distinctive persisted search and seizure phrase",
            mode,
            lambda prompt: prompts.append(prompt) or "analysis",
            db=db,
        )
        assert result["grounded_authority_count"] == 1
        assert result["authorities"][0]["corpus"] == "persisted_authorities"
        assert "321 Ga. 654" in prompts[0]
        assert "https://www.gasupreme.us/opinion/example" in prompts[0]


def test_persisted_unverified_authority_remains_visible_but_cannot_ground_ai(monkeypatch):
    db = _session()
    _add(db, citation="322 Ga. 100", text="distinctive identification evidence phrase", status="UNVERIFIED")
    _empty_file_corpus(monkeypatch)
    prompts = []

    result = service.grounded_legal_response(
        "distinctive identification evidence phrase",
        "case_analysis",
        lambda prompt: prompts.append(prompt) or "general guidance",
        db=db,
    )

    assert len(result["authorities"]) == 1
    assert result["authorities"][0]["citation"] == "322 Ga. 100"
    assert result["grounded_authority_count"] == 0
    assert "322 Ga. 100" not in prompts[0]


def test_persisted_negative_treatment_support_gate_cannot_be_bypassed(monkeypatch):
    db = _session()
    _add(
        db,
        citation="323 Ga. 200",
        text="distinctive suppression phrase",
        currency="current",
        precedent="unknown",
        negative="vacated",
    )
    _empty_file_corpus(monkeypatch)
    prompts = []

    result = service.grounded_legal_response(
        "distinctive suppression phrase",
        "motions",
        lambda prompt: prompts.append(prompt) or "general guidance",
        db=db,
    )

    assert len(result["authorities"]) == 1
    assert result["authorities"][0]["usable_as_support"] is False
    assert result["grounded_authority_count"] == 0
    assert "323 Ga. 200" not in prompts[0]
