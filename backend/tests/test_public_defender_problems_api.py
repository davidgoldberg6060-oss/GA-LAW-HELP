from fastapi.testclient import TestClient
from app.main import app
from app import language as lang
from app.anonymous_access import is_ai_path


def test_public_pd_endpoints_are_free_and_accurate():
    with TestClient(app) as client:
        g = client.get("/public/public-defender-problems")
        assert g.status_code == 200
        data = g.json()
        assert data["quick"] and data["sections"] and data["templates"]
        assert data["notice"] == lang.NOTICE_EN
        assert "O.C.G.A. § 9-14-42" in data["text"]
        assert "1 year" in data["text"] and "4 years" in data["text"]
        es = client.get("/public/public-defender-problems", params={"language": "es"}).json()
        assert es["language"] == "es" and es["notice"] == lang.NOTICE_ES
        offices = client.get("/public/public-defender-offices", params={"q": "Fulton"}).json()
        assert offices["office_count"] == 51
        assert offices["offices"][0]["circuit"] == "Atlanta Circuit"
        assert offices["bar_directory"]["url"].startswith("https://www.gabar.org/member-directory")
        assert "win/loss" in offices["outcome_note"].lower() or "per-attorney" in offices["outcome_note"]
        assert not is_ai_path("GET", "/public/public-defender-problems")
        assert not is_ai_path("GET", "/public/public-defender-offices")
