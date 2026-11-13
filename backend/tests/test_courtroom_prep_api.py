from fastapi.testclient import TestClient
from app.main import app
from app import language as lang
from app.anonymous_access import is_ai_path


def test_public_courtroom_prep_is_free_and_tailored():
    with TestClient(app) as client:
        general = client.get("/public/courtroom-prep")
        assert general.status_code == 200
        data = general.json()
        assert data["quick"] and data["sections"] and data["notice"] == lang.NOTICE_EN
        dui = client.get("/public/courtroom-prep", params={"case_type": "dui", "language": "en"}).json()
        assert dui["case_type"] == "dui"
        assert "DUI" in dui["title"]
        es = client.get("/public/courtroom-prep", params={"case_type": "eviction", "language": "es"}).json()
        assert es["language"] == "es" and es["notice"] == lang.NOTICE_ES
        voices = client.get("/public/voices")
        assert voices.status_code == 200
        ids = [v["id"] for v in voices.json()["voices"]]
        assert ids == ["off", "butler", "nanny"]


def test_plan_pdf_endpoint_returns_a_pdf():
    with TestClient(app) as client:
        r = client.post("/public/plan-pdf", json={
            "title": "Your Defense Plan: DUI",
            "text": "Quick answer\nChallenge the stop.\n\nQuestions to ask your lawyer\n• Can the blood test be challenged?\n\nO.C.G.A. § 40-6-391",
        })
        assert r.status_code == 200
        assert r.content.startswith(b"%PDF-1.4")
        assert "application/pdf" in r.headers["content-type"]
        empty = client.post("/public/plan-pdf", json={"title": "x", "text": ""})
        assert empty.status_code == 400


def test_translate_path_is_rate_limited():
    assert is_ai_path("POST", "/documents/translate")
    assert not is_ai_path("GET", "/public/courtroom-prep")
