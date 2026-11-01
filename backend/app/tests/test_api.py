import os
import tempfile
import hashlib
import hmac
import json
import time
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="galawhelp-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'api.db'}"
os.environ["EVIDENCE_DIR"] = str(_tmp / "evidence")
os.environ["JWT_SECRET"] = "unit-test-secret-that-is-longer-than-32-characters"
os.environ["ADMIN_EMAILS"] = "admin@example.com"
os.environ["PAID_ACCESS_EMAILS"] = "user@example.com"
os.environ["DEV_EXPOSE_RESET_TOKEN"] = "true"
os.environ["DEV_EXPOSE_VERIFICATION_TOKEN"] = "true"
os.environ["REQUIRE_VERIFIED_EMAIL"] = "false"

from fastapi.testclient import TestClient
from app.main import app


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_end_to_end_owner_security_evidence_and_authority(monkeypatch):
    with TestClient(app) as client:
        assert client.get("/health/live").json() == {"status": "ok"}
        assert client.get("/health/ready").json() == {"status": "ready", "database": "ok"}
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

        listed = client.get(f"/cases/{case_id}/evidence", headers=user_headers)
        assert listed.status_code == 200
        assert listed.json()[0]["filename"] == "record.txt"
        downloaded = client.get(f"/cases/{case_id}/evidence/{evidence_id}/download", headers=user_headers)
        assert downloaded.status_code == 200
        assert downloaded.content == b"immutable evidence bytes"
        assert downloaded.headers["x-content-sha256"] == uploaded.json()["sha256"]
        assert client.get(f"/cases/{case_id}/evidence/{evidence_id}/download", headers=admin_headers).status_code == 404

        denied = client.post("/legal/authorities", headers=user_headers, json={"authority_type": "case", "citation": "1 Ga. 1"})
        assert denied.status_code == 403
        authority = client.post("/legal/authorities", headers=admin_headers, json={"authority_type": "case", "citation": "1 Ga. 1", "title": "Verified test authority", "status": "CURRENT", "source_url": "https://www.gasupreme.us/"})
        assert authority.status_code == 200
        authority_id = authority.json()["id"]
        linked = client.post(f"/cases/{case_id}/authorities", headers=user_headers, json={"authority_id": authority_id, "proposition": "Test proposition", "verified": True})
        assert linked.status_code == 200
        assert client.get(f"/cases/{case_id}/why", headers=user_headers).json()["why"][0]["citation"] == "1 Ga. 1"

        captured = {}
        def fake_ai(prompt: str) -> str:
            captured["prompt"] = prompt
            return "Potential defense strategy review"
        monkeypatch.setattr("app.main.ask_openai", fake_ai)
        defense = client.post(f"/cases/{case_id}/defense-analysis", headers=user_headers, json={})
        assert defense.status_code == 200
        assert defense.json()["analysis"] == "Potential defense strategy review"
        assert defense.json()["linked_authorities"][0]["citation"] == "1 Ga. 1"
        assert defense.json()["linked_authorities"][0]["verified_for_prompt"] is True
        assert "1 Ga. 1" in captured["prompt"]

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


def test_free_launch_account_can_use_normal_authenticated_api():
    with TestClient(app) as client:
        free = client.post("/auth/register", json={"email": "free@example.com", "password": "free-account-secure-password"})
        assert free.status_code == 200
        headers = auth_header(free.json()["access_token"])
        assert client.get("/public/research", params={"q": "Georgia arrest law"}, headers=headers).status_code == 200
        assert client.post("/public/ask", json={"question": "What are my rights?"}, headers=headers).status_code != 403
        assert client.get("/cases", headers=headers).status_code == 200
        assert client.get("/me", headers=headers).status_code == 200
        assert client.get("/health/live").status_code == 200


def test_signed_billing_webhook_activates_membership():
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_unit_test"
    with TestClient(app) as client:
        account = client.post("/auth/register", json={"email": "billing@example.com", "password": "billing-account-secure-password"}).json()
        headers = auth_header(account["access_token"])
        profile = client.get("/me", headers=headers).json()
        assert profile["role"] == "user"
        event = {"id":"evt_test_paid","type":"checkout.session.completed","data":{"object":{"client_reference_id":str(profile["id"]),"metadata":{"user_id":str(profile["id"])}}}}
        payload = json.dumps(event, separators=(",", ":")).encode()
        timestamp = int(time.time())
        digest = hmac.new(b"whsec_unit_test", str(timestamp).encode() + b"." + payload, hashlib.sha256).hexdigest()
        response = client.post("/billing/webhook", content=payload, headers={"Stripe-Signature":f"t={timestamp},v1={digest}","Content-Type":"application/json"})
        assert response.status_code == 200
        assert client.get("/me", headers=headers).json()["role"] == "paid"
        assert client.get("/cases", headers=headers).status_code == 200
        bad = client.post("/billing/webhook", content=payload, headers={"Stripe-Signature":f"t={timestamp},v1=bad"})
        assert bad.status_code == 400


def test_privacy_policy_is_served_and_matches_docs():
    root = Path(__file__).resolve().parents[3]
    assert (root / "docs/PRIVACY_POLICY.md").read_text(encoding="utf-8") == (root / "backend/app/privacy_policy.md").read_text(encoding="utf-8")
    with TestClient(app) as client:
        page = client.get("/privacy")
        assert page.status_code == 200 and page.headers["content-type"].startswith("text/html")
        assert "<h1>GA.LAW.HELP Privacy Policy</h1>" in page.text and "Delete Account" in page.text
        assert client.get("/privacy.md").text.startswith("# GA.LAW.HELP Privacy Policy")


def test_account_deletion_removes_user_cases_files_and_tokens():
    from app import models
    from app.database import SessionLocal
    with TestClient(app) as client:
        reg = client.post("/auth/register", json={"email": "delete-me@example.com", "password": "delete-me-correct-password"}).json()
        if "dev_verification_token" in reg:
            client.post("/auth/verify-email", json={"token": reg["dev_verification_token"]})
        reg.update(client.post("/auth/login", json={"email": "delete-me@example.com", "password": "delete-me-correct-password"}).json())
        headers = auth_header(reg["access_token"])
        case_id = client.post("/cases", json={"title": "Case to delete"}, headers=headers).json()["id"]
        up = client.post(f"/cases/{case_id}/evidence", files={"file": ("doc.txt", b"evidence bytes", "text/plain")}, headers=headers)
        assert up.status_code == 200
        with SessionLocal() as db:
            key = db.query(models.Evidence).filter_by(case_id=case_id).one().storage_key
        stored = Path(os.environ["EVIDENCE_DIR"]) / "staging" / key
        assert stored.exists()

        assert client.post("/me/delete", json={"password": "delete-me-correct-password", "confirm": "nope"}, headers=headers).status_code == 422
        assert client.post("/me/delete", json={"password": "wrong-password-here", "confirm": "DELETE"}, headers=headers).status_code == 403
        done = client.post("/me/delete", json={"password": "delete-me-correct-password", "confirm": "DELETE"}, headers=headers)
        assert done.status_code == 200 and done.json() == {"deleted": True, "cases_deleted": 1, "files_deleted": 1}

        assert not stored.exists()
        assert client.get("/me", headers=headers).status_code == 401
        assert client.post("/auth/refresh", json={"refresh_token": reg["refresh_token"]}).status_code == 401
        assert client.post("/auth/login", json={"email": "delete-me@example.com", "password": "delete-me-correct-password"}).status_code == 401
        with SessionLocal() as db:
            assert db.query(models.Case).filter_by(id=case_id).count() == 0
            assert db.query(models.CaseNote).filter_by(case_id=case_id).count() == 0
            assert db.query(models.Evidence).filter_by(case_id=case_id).count() == 0
            assert db.query(models.AuditLog).filter_by(user_id=reg["user"]["id"]).count() == 0
