from fastapi.testclient import TestClient
from app.main import app


def test_guest_can_load_encounter_pack_without_login():
    with TestClient(app) as client:
        response = client.get("/public/encounter", params={"situation": "traffic stop"})
        assert response.status_code == 200
        body = response.json()
        indexes = body.get("official_indexes") or []
        assert indexes and all(item["url"].startswith("https://") for item in indexes)
        payload = response.json()
        assert payload["guest"] is True
        assert "disclaimer" in payload


def test_guest_rights_assistant_does_not_require_login(monkeypatch):
    def fake_ai(prompt: str) -> str:
        return (
            "SITUATION\nTraffic stop described by the guest.\n"
            "RIGHTS THAT MAY APPLY\nYou may remain silent and ask if you are free to leave.\n"
            "LAW ENFORCEMENT AUTHORITY\nOfficers may ask for license and registration during a lawful stop.\n"
            "LAW ENFORCEMENT LIMITS\nDo not treat this as a complete statement of current Georgia law.\n"
            "LAWFUL OPTIONS\nStay calm, do not resist, and do not destroy evidence.\n"
            "VERIFIED GEORGIA AUTHORITY\nNo matching verified indexed authority was supplied.\n"
            "IMPORTANT LIMITATIONS\nThis is general information, not legal advice."
        )

    monkeypatch.setattr("app.main.ask_openai", fake_ai)
    with TestClient(app) as client:
        response = client.post("/public/rights-assistant", json={"query": "What should I do at a traffic stop?", "mode": "rights"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["mode"] == "rights"
        assert "analysis" in payload


def test_private_cases_still_require_login():
    with TestClient(app) as client:
        assert client.get("/cases").status_code in {401, 403}

def test_guest_rights_falls_back_when_database_is_unavailable(monkeypatch):
    from sqlalchemy.exc import OperationalError

    def boom(*args, **kwargs):
        raise OperationalError("select", {}, Exception("database unavailable"))

    monkeypatch.setattr("app.main.grounded_legal_response", boom)
    with TestClient(app) as client:
        response = client.post("/public/rights-assistant", json={"query": "traffic stop rights", "mode": "rights"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["guest"] is True
        assert payload["login_required"] is False
        assert payload["authorities"] == []
        notice = payload["coverage_notice"].lower()
        assert "not a claim that any rule is current georgia law" in notice
        assert "do not resist" in notice

