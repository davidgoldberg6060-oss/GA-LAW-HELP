import os
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="galawhelp-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'api.db'}"
os.environ["EVIDENCE_DIR"] = str(_tmp / "evidence")
os.environ["JWT_SECRET"] = "unit-test-secret-that-is-longer-than-32-characters"
os.environ["ADMIN_EMAILS"] = "admin@example.com"
os.environ["DEV_EXPOSE_RESET_TOKEN"] = "true"
os.environ["DEV_EXPOSE_VERIFICATION_TOKEN"] = "true"
os.environ["REQUIRE_VERIFIED_EMAIL"] = "false"

from fastapi.testclient import TestClient
from app.main import app


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_end_to_end_owner_security_evidence_and_authority():
    with TestClient(app) as client:
        admin = client.post("/auth/register", json={"email": "admin@example.com", "password": "correct-horse-battery"})
        assert admin.status_code == 200
        admin_json = admin.json()
        admin_headers = auth_header(admin_json["access_token"])

        user = client.post("/auth/register", json={"email": "user@example.com", "password": "another-correct-password"})
        assert user.status_code == 200
        user_json = user.json()
        user_headers = auth_header(user_json["access_token"])

        verified = client.post("/auth/verify-email", json={"token": user_json["dev_verification_token"]})
        assert verified.status_code == 200
        assert verified.json()["verified"] is True
        assert client.get("/me", headers=user_headers).json()["verified_at"] is not None

        created = client.post("/cases", headers=user_headers, json={"title": "Appeal review", "county": "Fulton", "stage": "appeal", "narrative": "Sentenced after a guilty plea"})
        assert created.status_code == 200
        case_id = created.json()["id"]

        updated = client.patch(f"/cases/{case_id}", headers=user_headers, json={"stage": "habeas"})
        assert updated.status_code == 200
        assert updated.json()["stage"] == "habeas"

        assert client.get(f"/cases/{case_id}", headers=admin_headers).status_code == 404

        uploaded = client.post(
            f"/cases/{case_id}/evidence",
            headers=user_headers,
            files={"file": ("record.txt", b"immutable evidence bytes", "text/plain")},
        )
        assert uploaded.status_code == 200
        evidence_id = uploaded.json()["id"]
        verified = client.post(f"/cases/{case_id}/evidence/{evidence_id}/verify", headers=user_headers)
        assert verified.status_code == 200
        assert verified.json()["verified"] is True

        denied = client.post("/legal/authorities", headers=user_headers, json={"authority_type": "case", "citation": "1 Ga. 1"})
        assert denied.status_code == 403
        authority = client.post("/legal/authorities", headers=admin_headers, json={"authority_type": "case", "citation": "1 Ga. 1", "title": "Verified test authority"})
        assert authority.status_code == 200
        authority_id = authority.json()["id"]
        linked = client.post(f"/cases/{case_id}/authorities", headers=user_headers, json={"authority_id": authority_id, "proposition": "Test proposition"})
        assert linked.status_code == 200
        assert client.get(f"/cases/{case_id}/why", headers=user_headers).json()["why"][0]["citation"] == "1 Ga. 1"

        refreshed = client.post("/auth/refresh", json={"refresh_token": user_json["refresh_token"]})
        assert refreshed.status_code == 200
        new_refresh = refreshed.json()["refresh_token"]
        assert client.post("/auth/logout", json={"refresh_token": new_refresh}).json()["logged_out"] is True
        assert client.post("/auth/refresh", json={"refresh_token": new_refresh}).status_code == 401


def test_password_reset_revokes_sessions_and_hides_unknown_accounts():
    with TestClient(app) as client:
        account = client.post("/auth/register", json={"email": "reset@example.com", "password": "correct-horse-battery"}).json()
        assert client.post("/auth/forgot-password", json={"email": "missing@example.com"}).json() == {"accepted": True}
        reset = client.post("/auth/forgot-password", json={"email": "reset@example.com"}).json()
        assert reset["accepted"] is True
        assert client.post("/auth/reset-password", json={"token": reset["dev_reset_token"], "new_password": "new-correct-horse-battery"}).status_code == 200
        assert client.post("/auth/refresh", json={"refresh_token": account["refresh_token"]}).status_code == 401
        assert client.post("/auth/login", json={"email": "reset@example.com", "password": "correct-horse-battery"}).status_code == 401
        assert client.post("/auth/login", json={"email": "reset@example.com", "password": "new-correct-horse-battery"}).status_code == 200
