import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import loophole_analysis_service as svc, models

HITS = [
    {"citation": "O.C.G.A. § 16-3-21", "title": "Use of force in defense", "source_url": "https://law.example/16-3-21", "verification_status": "verified", "record_type": "statute"},
    {"citation": "O.C.G.A. § 16-3-23.1", "title": "No duty to retreat", "source_url": "https://law.example/16-3-23.1", "verification_status": "verified", "record_type": "statute"},
]


def _retrieval(hits):
    return lambda query, mode, db=None, limit=12: {"hits": list(hits)}


def _ai(payload):
    return lambda prompt: "```json\n" + json.dumps(payload) + "\n```"


def test_drops_findings_with_unretrieved_citations(monkeypatch):
    monkeypatch.setattr(svc, "_hybrid_retrieval", _retrieval(HITS))
    payload = {"findings": [
        {"type": "exception", "title": "Forcible felony", "explanation": "Deadly force allowed to prevent a forcible felony.", "citations": ["O.C.G.A. § 16-3-21"]},
        {"type": "contradiction", "title": "Fake", "explanation": "Invented.", "citations": ["O.C.G.A. § 99-9-99"]},
        {"type": "gap", "title": "Mixed", "explanation": "Mixed cites.", "citations": ["O.C.G.A. § 16-3-23.1", "Smith v. State, 1 Ga. 1"]},
        {"type": "ambiguity", "title": "No cite", "explanation": "None.", "citations": []},
        {"type": "loophole", "title": "Bad type", "explanation": "x", "citations": ["O.C.G.A. § 16-3-21"]},
    ], "lawyer_take": {"text": "Write down what happened. Talk to a Georgia attorney.", "citations": ["O.C.G.A. § 16-3-21"]}}
    result = svc.analyze_loopholes("self-defense", _ai(payload))
    assert [f["title"] for f in result["findings"]] == ["Forcible felony"]
    assert result["findings"][0]["type_label"] == "Exception"
    assert result["findings"][0]["citations"][0]["source_url"] == "https://law.example/16-3-21"
    assert result["dropped_findings"] == 4
    assert result["disclaimer"] == svc.DISCLAIMER
    take = result["lawyer_take"]
    assert take["label"] == "If I Was Your Lawyer, I Would Say"
    assert take["disclaimer"].startswith("Not legal advice")
    assert take["citations"][0]["citation"] == "O.C.G.A. § 16-3-21"


def test_lawyer_take_with_invented_citation_is_dropped(monkeypatch):
    monkeypatch.setattr(svc, "_hybrid_retrieval", _retrieval(HITS))
    payload = {"findings": [], "lawyer_take": {"text": "Do this.", "citations": ["Made Up v. State"]}}
    result = svc.analyze_loopholes("self-defense", _ai(payload))
    assert result["lawyer_take"] is None
    assert result["findings"] == [] and result["message"] == svc.NONE_FOUND


def test_no_verified_authority_says_so_without_calling_model(monkeypatch):
    monkeypatch.setattr(svc, "_hybrid_retrieval", _retrieval([{"citation": "X", "verification_status": "unverified", "source_url": "https://x"}]))
    result = svc.analyze_loopholes("landlord deposits", lambda p: pytest.fail("model called"))
    assert result["findings"] == [] and "No verified Georgia authority" in result["message"]


def test_refuses_evasion_requests():
    result = svc.analyze_loopholes("how to evade police after a DUI", lambda p: pytest.fail("model called"))
    assert result["refused"] is True and result["findings"] == []
    with pytest.raises(ValueError):
        svc.analyze_loopholes("  ", lambda p: p)


def test_route_requires_auth_and_returns_findings(monkeypatch):
    from app.auth import current_user
    from app.database import Base, get_db
    from app.main import app
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        user = models.User(email="u@example.com", password_hash="x", role="paid"); db.add(user); db.commit(); uid = user.id
    def override_db():
        with Session() as db:
            yield db
    def override_user():
        with Session() as db:
            return db.get(models.User, uid)
    monkeypatch.setattr(svc, "_hybrid_retrieval", _retrieval(HITS))
    import app.main as main
    monkeypatch.setattr(main, "ask_openai", _ai({"findings": [{"type": "gap", "title": "t", "explanation": "e", "citations": ["O.C.G.A. § 16-3-21"]}]}))
    with TestClient(app) as client:
        assert client.post("/loopholes/analyze", json={"topic": "self-defense"}).status_code in (401, 403)
        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[current_user] = override_user
        try:
            r = client.post("/loopholes/analyze", json={"topic": "self-defense"})
            assert r.status_code == 200, r.text
            assert r.json()["findings"][0]["type"] == "gap"
            assert client.post("/loopholes/analyze", json={"topic": ""}).status_code == 400
        finally:
            app.dependency_overrides.clear()
