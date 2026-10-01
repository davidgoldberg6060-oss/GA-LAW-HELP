"""Release guard: the live motion-screen endpoint must use verified authority orchestration."""
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

MAIN = Path(__file__).resolve().parents[1] / "main.py"


def test_live_motion_screen_uses_verified_registry_service():
    source = MAIN.read_text()
    assert "from .motion_screen_service import motion_screen_response" in source
    route = source.split("def private_motion_screen", 1)[1].split("@app.", 1)[0]
    # The live route must stay on the verified authority service. The AI callable
    # may be the public wrapper or the delegated wrapper used during incremental
    # endpoint migration, so guard the service call rather than one exact symbol.
    assert "motion_screen_response(db,facts," in route.replace(" ", "")
    assert "verification_mode" not in route  # response contract belongs to the service
    assert "prompt='GEORGIA CRIMINAL CASE MOTION SCREEN" not in route
    assert "RUN_MOTION_SCREEN" in route
    assert "temporarily unavailable" in route


def test_live_motion_screen_returns_verified_registry_contract(monkeypatch):
    def fake_ai(prompt: str) -> str:
        assert "VERIFIED MOTION REGISTRY" in prompt
        assert "Do not invent" in prompt or "do not invent" in prompt
        return (
            "Research lead only. No matching verified motion authority was supplied. "
            "Do not treat this as a current Georgia citation. Stay with the record; "
            "do not resist, lie, or destroy evidence."
        )

    monkeypatch.setattr("app.main.ask_openai", fake_ai)
    with TestClient(app) as client:
        denied = client.post("/cases/1/motion-screen", json={"additional_facts": "traffic stop"})
        assert denied.status_code in {401, 403}

        registered = client.post(
            "/auth/register",
            json={"email": "motion-screen@example.com", "password": "correct-horse-battery"},
        )
        assert registered.status_code == 200, registered.text
        token = registered.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        created = client.post(
            "/cases",
            headers=headers,
            json={
                "title": "Private motion screen",
                "county": "Fulton",
                "case_type": "criminal",
                "stage": "pretrial",
                "narrative": "User-supplied facts only. No official citation is claimed.",
            },
        )
        assert created.status_code == 200, created.text
        case_id = created.json()["id"]
        response = client.post(
            f"/cases/{case_id}/motion-screen",
            headers=headers,
            json={"additional_facts": "Possible search issue. Verify the record before any filing."},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["verification_mode"] == "VERIFIED_REGISTRY_ONLY"
        assert "authority_coverage" in body
        assert "analysis" in body
        assert "Ga." not in body["analysis"]
        assert "not legal advice" in body["notice"].lower()
