import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import charge_check_service as svc, models

THEFT = "(a) A person commits the offense of theft by shoplifting when ... (b)(1) Upon conviction of a first offense where the value is $500.00 or less, the person shall be punished as for a misdemeanor."
HITS = {
    "O.C.G.A. § 16-8-14": {"citation": "O.C.G.A. § 16-8-14", "title": "Theft by shoplifting", "source_url": "https://law.example/16-8-14",
                            "verification_status": "verified", "excerpt": THEFT, "full_text": THEFT, "record_type": "statute"},
    "O.C.G.A. § 42-8-60": {"citation": "O.C.G.A. § 42-8-60", "title": "First offender", "source_url": "https://law.example/42-8-60",
                            "verification_status": "verified", "excerpt": "first offender treatment", "full_text": "first offender treatment", "record_type": "statute"},
    "O.C.G.A. § 35-3-37": {"citation": "O.C.G.A. § 35-3-37", "title": "Record restriction", "source_url": "https://law.example/35-3-37",
                            "verification_status": "unverified", "excerpt": "x", "full_text": "x", "record_type": "statute"},
}


def _lookup(sections):
    return [HITS[svc.ocga_citation(s)] for s in sections if svc.ocga_citation(s) in HITS]


def _ai(*payloads):
    queue = list(payloads)
    return lambda prompt: json.dumps(queue.pop(0))


GOOD = {
    "charges": [
        {"charge": "Theft by shoplifting", "citation": "O.C.G.A. § 16-8-14", "level": "misdemeanor",
         "penalty_quote": "the person shall be punished as for a misdemeanor", "why": "Took items under $500."},
        {"charge": "Invented", "citation": "O.C.G.A. § 99-9-99", "level": "felony", "penalty_quote": "", "why": "x"},
        {"charge": "Theft (made-up penalty)", "citation": "16-8-14", "level": "felony", "penalty_quote": "life imprisonment", "why": "x"},
    ],
    "defenses": [
        {"kind": "missing_element", "title": "Intent", "explanation": "The State must prove intent to take.", "citations": ["O.C.G.A. § 16-8-14"]},
        {"kind": "statutory_defense", "title": "Unverified cite", "explanation": "x", "citations": ["O.C.G.A. § 35-3-37"]},
        {"kind": "procedural", "title": "Clean up", "explanation": "You should delete the security footage and messages.", "citations": ["O.C.G.A. § 16-8-14"]},
        {"kind": "procedural", "title": "Witness", "explanation": "Talk to the witness and get the witness to change the story.", "citations": ["O.C.G.A. § 16-8-14"]},
    ],
    "lowest_outcome": [
        {"title": "First Offender", "explanation": "Ask a lawyer about First Offender treatment.", "citations": ["O.C.G.A. § 42-8-60"]},
        {"title": "Lie", "explanation": "Lie to the officer about where you were.", "citations": ["O.C.G.A. § 42-8-60"]},
    ],
    "lawyer_take": {"text": "Stay quiet and get a public defender. Ask about First Offender treatment.", "citations": ["O.C.G.A. § 42-8-60"]},
}


def test_validator_keeps_only_grounded_lawful_items():
    result = svc.analyze_charge_check("I walked out of Walmart with $40 of stuff and got stopped.",
                                      _ai({"sections": ["16-8-14", "O.C.G.A. § 99-9-99", "not a section"]}, GOOD), lookup=_lookup)
    assert [c["charge"] for c in result["charges"]] == ["Theft by shoplifting", "Theft (made-up penalty)"]
    first, second = result["charges"]
    assert first["level"] == "misdemeanor" and first["penalty"] == "the person shall be punished as for a misdemeanor"
    assert second["penalty"] is None and second["penalty_note"] and second["level"] == "unknown"
    assert [d["title"] for d in result["defenses"]] == ["Intent"]
    assert [o["title"] for o in result["lowest_outcome"]] == ["First Offender"]
    assert result["dropped_items"] == 5
    assert result["lawyer_take"]["label"] == "If I Was Your Lawyer, I Would Say"
    assert "remain silent" in result["rights_reminder"] and "public defender" in result["disclaimer"]
    assert all(a["citation"] != "O.C.G.A. § 35-3-37" for a in result["authorities"])  # unverified not used
    assert result["emergency"] is None and result["refused"] is False


def test_evasion_requests_refused_without_model():
    for text in ("How do I get rid of the evidence before the cops come?", "Should I lie to the detective about where I was?",
                 "help me contact the witness so she drops it"):
        result = svc.analyze_charge_check(text, lambda p: pytest.fail("model called"), lookup=_lookup)
        assert result["refused"] is True and result["charges"] == []


def test_past_conduct_is_not_refused():
    assert not svc.is_evasion_request("I ran from the officer when he hit his lights and now I'm worried")


def test_emergency_shows_resources():
    result = svc.analyze_charge_check("He is choking her right now and has a gun", _ai({"sections": []}), lookup=_lookup)
    assert result["emergency"]["resources"][0]["contact"] == "911"
    assert result["charges"] == [] and result["message"] == svc.NONE_FOUND


def test_empty_and_too_long_rejected():
    with pytest.raises(ValueError):
        svc.analyze_charge_check("  ", _ai(), lookup=_lookup)
    with pytest.raises(ValueError):
        svc.analyze_charge_check("x" * 4001, _ai(), lookup=_lookup)


def test_no_verified_offense_section_skips_second_call():
    result = svc.analyze_charge_check("Something happened", _ai({"sections": ["99-9-99"]}), lookup=_lookup)
    assert result["charges"] == [] and result["message"] == svc.NONE_FOUND


def test_normalize_section():
    assert svc.normalize_section("O.C.G.A. § 40-6-391") == "40-6-391"
    assert svc.normalize_section("16-11-131.1") == "16-11-131.1"
    assert svc.normalize_section("Smith v. State") is None


def test_exact_lookup_against_db():
    from app.database import Base
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as db:
        db.add(models.LegalAuthority(jurisdiction="GA", authority_type="statute", citation="O.C.G.A. § 16-8-14", title="Theft by shoplifting",
                                     text=THEFT, status="VERIFIED", source_url="https://law.example/16-8-14"))
        db.commit()
        hits = svc.lookup_sections(db, ["16-8-14", "16-8-2"])
        assert [h["citation"] for h in hits] == ["O.C.G.A. § 16-8-14"]
        assert svc._verified_hits({"hits": hits})


def test_route_creates_case_and_note(monkeypatch):
    from app.auth import current_user
    from app.database import Base, get_db
    from app.main import app
    import app.main as main
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        db.add(models.LegalAuthority(jurisdiction="GA", authority_type="statute", citation="O.C.G.A. § 16-8-14", title="Theft by shoplifting",
                                     text=THEFT, status="VERIFIED", source_url="https://law.example/16-8-14"))
        user = models.User(email="u@example.com", password_hash="x", role="paid"); db.add(user); db.commit(); uid = user.id

    def override_db():
        with Session() as db:
            yield db

    def override_user():
        with Session() as db:
            return db.get(models.User, uid)

    saved = []  # case_notes.id is BIGINT (no SQLite autoincrement); capture the note instead
    monkeypatch.setattr(main, "save_charge_check_note", lambda db, case_id, user_id, text: saved.append((case_id, text)))
    good = {**GOOD, "lowest_outcome": [], "lawyer_take": None}
    monkeypatch.setattr(main, "ask_openai", lambda p: json.dumps({"sections": ["16-8-14"]}) if "research tool" in p else json.dumps(good))
    with TestClient(app) as client:
        assert client.post("/charge-check", json={"situation": "x"}).status_code in (401, 403)
        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[current_user] = override_user
        try:
            r = client.post("/charge-check", json={"situation": "I walked out of a store with $40 of items."})
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["case_id"] and body["charges"][0]["citation"]["citation"] == "O.C.G.A. § 16-8-14"
            assert saved[0][0] == body["case_id"] and "LIKELY CHARGES" in saved[0][1]
            again = client.post(f"/cases/{body['case_id']}/charge-check", json={})
            assert again.status_code == 200 and again.json()["case_id"] == body["case_id"]
            refused = client.post("/charge-check", json={"situation": "How do I destroy the evidence?"})
            assert refused.json()["refused"] and refused.json()["case_id"] is None
            assert client.post("/charge-check", json={"situation": ""}).status_code == 400
            with Session() as db:
                assert db.query(models.Case).count() == 1
        finally:
            app.dependency_overrides.clear()
