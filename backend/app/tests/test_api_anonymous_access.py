import os
import secrets
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="galawhelp-anon-"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp / 'anon.db'}")
os.environ.setdefault("EVIDENCE_DIR", str(_tmp / "evidence"))
os.environ.setdefault("JWT_SECRET", "unit-test-secret-that-is-longer-than-32-characters")

import pytest
from fastapi.testclient import TestClient

from app import anonymous_access
from app.anonymous_access import DailyCounter, anonymous_email, is_ai_path
from app.main import app


@pytest.fixture(autouse=True)
def _reset_limits():
    anonymous_access.ai_counter.reset()
    anonymous_access.anon_create_counter.reset()
    yield
    anonymous_access.ai_counter.reset()
    anonymous_access.anon_create_counter.reset()


def _key() -> str:
    return secrets.token_urlsafe(32)


def _session(client, key, ip="10.0.0.1"):
    r = client.post("/auth/anonymous", json={"device_key": key}, headers={"X-Real-IP": ip})
    assert r.status_code == 200, r.text
    return r.json()


def test_anonymous_session_is_created_once_and_reused():
    with TestClient(app) as client:
        key = _key()
        first = _session(client, key)
        assert first["anonymous"] is True and first["created"] is True and first["access_token"]
        again = _session(client, key)
        assert again["created"] is False and again["user"]["id"] == first["user"]["id"]
        me = client.get("/me", headers={"Authorization": "Bearer " + again["access_token"]}).json()
        assert me["anonymous"] is True and me["email"] is None


def test_short_or_malformed_device_key_is_rejected():
    with TestClient(app) as client:
        assert client.post("/auth/anonymous", json={"device_key": "short"}).status_code == 422
        assert client.post("/auth/anonymous", json={"device_key": "x" * 40 + "!"}).status_code == 422


def test_cases_stay_private_per_device_and_device_can_delete_its_data():
    with TestClient(app) as client:
        key_a, key_b = _key(), _key()
        a = {"Authorization": "Bearer " + _session(client, key_a)["access_token"]}
        b = {"Authorization": "Bearer " + _session(client, key_b)["access_token"]}
        case = client.post("/cases", headers=a, json={"title": "Traffic stop", "narrative": "Pulled over"})
        assert case.status_code == 200
        cid = case.json()["id"]
        assert client.get(f"/cases/{cid}", headers=b).status_code == 404
        assert all(c["id"] != cid for c in client.get("/cases", headers=b).json())
        assert client.get(f"/cases/{cid}", headers=a).status_code == 200
        deleted = client.post("/me/delete", headers=a, json={"password": key_a, "confirm": "DELETE"})
        assert deleted.status_code == 200 and deleted.json()["cases_deleted"] == 1
        assert client.get("/me", headers=a).status_code == 401


def test_anonymous_creation_is_capped_per_ip(monkeypatch):
    monkeypatch.setattr(anonymous_access, "ANON_CREATE_IP_DAILY_LIMIT", 2)
    with TestClient(app) as client:
        _session(client, _key(), ip="10.9.9.9")
        _session(client, _key(), ip="10.9.9.9")
        r = client.post("/auth/anonymous", json={"device_key": _key()}, headers={"X-Real-IP": "10.9.9.9"})
        assert r.status_code == 429
        _session(client, _key(), ip="10.9.9.10")


def test_ai_endpoints_are_capped_per_device_with_friendly_message(monkeypatch):
    monkeypatch.setattr(anonymous_access, "AI_DEVICE_DAILY_LIMIT", 2)
    with TestClient(app) as client:
        h = {"Authorization": "Bearer " + _session(client, _key())["access_token"], "X-Real-IP": "10.1.1.1"}
        for _ in range(2):
            assert client.post("/loopholes/analyze", headers=h, json={"topic": ""}).status_code != 429
        blocked = client.post("/loopholes/analyze", headers=h, json={"topic": ""})
        assert blocked.status_code == 429
        assert "today's limit" in blocked.json()["detail"]
        # Non-AI endpoints are not limited.
        assert client.get("/cases", headers=h).status_code == 200


def test_guest_ai_endpoint_is_capped_per_ip(monkeypatch):
    monkeypatch.setattr(anonymous_access, "AI_IP_DAILY_LIMIT", 1)
    with TestClient(app) as client:
        assert client.post("/public/rights-assistant", json={"query": ""}, headers={"X-Real-IP": "10.2.2.2"}).status_code == 400
        assert client.post("/public/rights-assistant", json={"query": ""}, headers={"X-Real-IP": "10.2.2.2"}).status_code == 429
        assert client.post("/public/rights-assistant", json={"query": ""}, headers={"X-Real-IP": "10.2.2.3"}).status_code == 400


def test_ai_path_matcher_and_counter():
    assert is_ai_path("POST", "/cases/12/chat") and is_ai_path("POST", "/charge-check")
    assert not is_ai_path("GET", "/cases/12/chat") and not is_ai_path("POST", "/cases")
    c = DailyCounter()
    assert c.hit("k", 1, now=0) and not c.hit("k", 1, now=10) and c.hit("k", 1, now=86401)
    assert anonymous_email("a" * 40).endswith("@anonymous.galaw.invalid")
