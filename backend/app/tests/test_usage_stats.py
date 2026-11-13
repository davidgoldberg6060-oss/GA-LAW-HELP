import os
import secrets
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

_tmp = Path(tempfile.mkdtemp(prefix="galawhelp-stats-"))
# Don't clobber a sqlite URL or evidence dir already set by another test module or CI.
if not os.environ.get("DATABASE_URL", "").startswith("sqlite"):
    os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'stats.db'}"
os.environ.setdefault("EVIDENCE_DIR", str(_tmp / "evidence"))
os.environ.setdefault("JWT_SECRET", "unit-test-secret-that-is-longer-than-32-characters")
os.environ["STATS_ADMIN_TOKEN"] = "test-owner-stats-token-not-for-production"
os.environ["STATS_TZ"] = "America/New_York"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import usage_stats
from app.database import SessionLocal
from app.main import app
from app.usage_stats import FEEDBACK_CATEGORIES, hash_device


TOKEN = os.environ["STATS_ADMIN_TOKEN"]
TZ = ZoneInfo("America/New_York")


@pytest.fixture(autouse=True)
def _reset():
    usage_stats.reset_for_tests()
    db = SessionLocal()
    try:
        usage_stats.ensure_tables(db)
        db.execute(text("DELETE FROM usage_events"))
        db.execute(text("DELETE FROM app_feedback"))
        db.commit()
    finally:
        db.close()
    yield
    usage_stats.reset_for_tests()


def _key() -> str:
    return secrets.token_urlsafe(32)


def _auth(client, key=None, ip="10.0.0.2"):
    key = key or _key()
    r = client.post("/auth/anonymous", json={"device_key": key}, headers={"X-Real-IP": ip})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}, r.json()["user"]["id"], key


def _stats(client):
    r = client.get("/stats/summary", headers={"Authorization": "Bearer " + TOKEN})
    assert r.status_code == 200, r.text
    return r.json()


def test_usage_events_are_counted_by_platform_and_unique_device():
    with TestClient(app) as client:
        a, uid_a, _ = _auth(client, ip="10.1.0.1")
        b, uid_b, _ = _auth(client, ip="10.1.0.2")
        ev = {"platform": "web", "app_version": "0.1.0", "events": [
            {"type": "first_open"}, {"type": "install"}, {"type": "open"}, {"type": "session"},
            {"type": "feature", "feature": "chat"},
        ]}
        assert client.post("/usage/events", json=ev, headers=a).json()["accepted"] == 5
        ev["platform"] = "android"
        ev["app_version"] = "1.7.3"
        ev["events"] = [{"type": "open"}, {"type": "session"}, {"type": "feature", "feature": "funny_laws"}]
        assert client.post("/usage/events", json=ev, headers={**b, "X-App-Platform": "android"}).json()["accepted"] == 3
        summary = _stats(client)
        today = summary["today"]
        assert today["opens"]["web"] == 1 and today["opens"]["android"] == 1 and today["opens"]["total"] == 2
        assert today["sessions"]["total"] == 2
        assert today["unique_devices"] == 2
        assert today["first_opens"]["web"] == 1
        assert today["new_installs"]["web"] == 1
        assert today["features"]["chat"]["web"] == 1
        assert today["features"]["funny_laws"]["android"] == 1
        assert summary["timezone"] == "America/New_York"
        assert len(summary["daily"]) >= 1
        assert summary["daily"][-1]["opens"] == 2


def test_events_never_store_ip_question_text_or_raw_user_id():
    with TestClient(app, headers={"X-Real-IP": "203.0.113.9"}) as client:
        headers, uid, key = _auth(client, ip="203.0.113.9")
        client.post("/usage/events", json={
            "platform": "web",
            "events": [{"type": "open"}, {"type": "feature", "feature": "chat"}],
        }, headers=headers)
        db = SessionLocal()
        try:
            usage_stats.ensure_tables(db)
            rows = db.execute(text("SELECT event_type, platform, feature, device_hash, app_version FROM usage_events")).fetchall()
            cols = db.execute(text("PRAGMA table_info(usage_events)")).fetchall()
            names = {row[1] for row in cols}
        finally:
            db.close()
        assert "ip" not in names and "ip_address" not in names and "question" not in names and "user_id" not in names
        assert rows and all(row[3] == hash_device(uid) for row in rows)
        assert all(row[3] != str(uid) and row[3] != key for row in rows)
        assert "203.0.113.9" not in str(rows)


def test_invalid_events_are_ignored_and_ai_question_is_not_double_counted_from_the_client():
    with TestClient(app) as client:
        headers, _, _ = _auth(client)
        r = client.post("/usage/events", json={"platform": "web", "events": [
            {"type": "ai_question", "feature": "chat"},
            {"type": "feature", "feature": "not-a-feature"},
            {"type": "nope"},
            {"type": "open"},
        ]}, headers=headers)
        assert r.status_code == 200 and r.json()["accepted"] == 1
        today = _stats(client)["today"]
        assert today["opens"]["total"] == 1
        assert today["ai_questions"]["total"] == 0


def test_ai_requests_are_counted_without_storing_the_question(monkeypatch):
    with TestClient(app) as client:
        headers, _, _ = _auth(client)
        # Avoid calling the real model: the rights-assistant endpoint still runs after our
        # assertion that the body is not written to usage tables.
        from app.main import grounded_legal_response

        def fake_grounded(query, mode, ask, db=None, conversation=None):
            return {"answer": "This is general information.", "authorities": []}

        monkeypatch.setattr("app.main.grounded_legal_response", fake_grounded)
        r = client.post("/public/rights-assistant", json={"query": "SECRET-QUESTION-TEXT about a DUI", "mode": "general"}, headers=headers)
        assert r.status_code == 200, r.text
        db = SessionLocal()
        try:
            usage_stats.ensure_tables(db)
            dumped = str(db.execute(text("SELECT * FROM usage_events")).fetchall())
            rows = db.execute(text("SELECT event_type, feature FROM usage_events")).fetchall()
        finally:
            db.close()
        assert "SECRET-QUESTION-TEXT" not in dumped
        kinds = {(row[0], row[1]) for row in rows}
        assert ("ai_question", "chat") in kinds


def test_stats_endpoints_require_the_owner_token():
    with TestClient(app) as client:
        assert client.get("/stats/summary").status_code == 401
        assert client.get("/stats/summary", headers={"Authorization": "Bearer wrong-token"}).status_code == 401
        assert client.post("/stats/session").status_code == 401
        ok = client.post("/stats/session", headers={"X-Stats-Token": TOKEN})
        assert ok.status_code == 200 and ok.json()["ok"] is True
        page = client.get("/stats")
        assert page.status_code == 200
        assert "How people are using the app" in page.text
        assert TOKEN not in page.text
        assert "text/html" in page.headers["content-type"]


def test_stats_token_missing_is_unavailable(monkeypatch):
    monkeypatch.delenv("STATS_ADMIN_TOKEN", raising=False)
    with TestClient(app) as client:
        r = client.get("/stats/summary", headers={"Authorization": "Bearer " + TOKEN})
        assert r.status_code == 503


def test_feedback_is_stored_without_question_text_and_listed_on_stats():
    with TestClient(app) as client:
        headers, uid, _ = _auth(client)
        bad = client.post("/feedback", json={"platform": "android", "category": "nope", "rating": 3}, headers=headers)
        assert bad.status_code == 422
        empty = client.post("/feedback", json={"platform": "android", "category": "idea"}, headers=headers)
        assert empty.status_code == 422
        mail = client.post("/feedback", json={
            "platform": "android", "app_version": "1.7.3", "screen": "home",
            "category": "idea", "rating": 5, "comment": "A search box on Home would help.",
            "contact_email": "not-an-email",
        }, headers=headers)
        assert mail.status_code == 422
        # A "question" field must be ignored if a client sends one.
        ok = client.post("/feedback", json={
            "platform": "android", "app_version": "1.7.3", "screen": "home",
            "category": "idea", "rating": 4, "comment": "Love the app. A night-court map would help.",
            "contact_email": "treyvon@example.com", "question": "should never be stored",
        }, headers=headers)
        assert ok.status_code == 200 and ok.json()["ok"] is True
        other, _, _ = _auth(client, ip="10.2.0.2")
        client.post("/feedback", json={
            "platform": "web", "app_version": "0.1.0", "screen": "settings",
            "category": "bug", "comment": "The menu closed itself.",
        }, headers=other)
        db = SessionLocal()
        try:
            cols = {row[1] for row in db.execute(text("PRAGMA table_info(app_feedback)")).fetchall()}
            dumped = str(db.execute(text("SELECT * FROM app_feedback")).fetchall())
        finally:
            db.close()
        assert "question" not in cols
        assert "should never be stored" not in dumped
        fb = _stats(client)["feedback"]
        assert fb["count"] == 2
        assert fb["average_rating"] == 4.0
        assert fb["rating_count"] == 1
        assert fb["by_category"]["idea"] == 1 and fb["by_category"]["bug"] == 1
        comments = " ".join(row["comment"] or "" for row in fb["recent"])
        assert "night-court map" in comments and "menu closed" in comments
        emails = [row["contact_email"] for row in fb["recent"]]
        assert "treyvon@example.com" in emails
        assert all(row.get("device_hash") is None or "device_hash" not in row for row in fb["recent"])


def test_feedback_is_rate_limited_per_device(monkeypatch):
    monkeypatch.setattr(usage_stats, "FEEDBACK_DAILY_LIMIT", 2)
    with TestClient(app) as client:
        headers, _, _ = _auth(client)
        payload = {"platform": "web", "category": "other", "rating": 5, "comment": "ok"}
        assert client.post("/feedback", json=payload, headers=headers).status_code == 200
        assert client.post("/feedback", json=payload, headers=headers).status_code == 200
        third = client.post("/feedback", json=payload, headers=headers)
        assert third.status_code == 429
        other, _, _ = _auth(client, ip="10.3.0.3")
        assert client.post("/feedback", json=payload, headers=other).status_code == 200


def test_usage_event_rate_limit(monkeypatch):
    monkeypatch.setattr(usage_stats, "EVENT_DAILY_LIMIT", 2)
    with TestClient(app) as client:
        headers, _, _ = _auth(client)
        payload = {"platform": "web", "events": [{"type": "open"}]}
        assert client.post("/usage/events", json=payload, headers=headers).status_code == 200
        assert client.post("/usage/events", json=payload, headers=headers).status_code == 200
        assert client.post("/usage/events", json=payload, headers=headers).status_code == 429


def test_summary_windows_use_eastern_days():
    with TestClient(app) as client:
        headers, _, _ = _auth(client)
        now = datetime.now(timezone.utc)
        db = SessionLocal()
        try:
            # An event 20 days ago should appear in 30-day totals and the daily chart, not in 7-day totals.
            usage_stats.record_event(
                db, event_type="open", platform="web", device_hash="abc",
                occurred_at=(now - timedelta(days=20)).replace(tzinfo=None),
            )
            usage_stats.record_event(
                db, event_type="open", platform="android", device_hash="abc",
                occurred_at=(now - timedelta(days=2)).replace(tzinfo=None),
            )
        finally:
            db.close()
        summary = _stats(client)
        assert summary["last_7_days"]["opens"]["total"] == 1
        assert summary["last_30_days"]["opens"]["total"] == 2
        days = {row["day"] for row in summary["daily"]}
        assert len(summary["daily"]) >= 30
        eastern_20 = (now - timedelta(days=20)).astimezone(TZ).date().isoformat()
        assert eastern_20 in days


def test_privacy_policy_mentions_anonymous_usage_and_feedback():
    with TestClient(app) as client:
        page = client.get("/privacy")
        assert page.status_code == 200
        text = page.text
        assert "Anonymous usage counts" in text
        assert "Optional app feedback" in text
        assert "one-way hash" in text
        assert "third-party advertising or analytics trackers" in text
        md = Path(__file__).resolve().parents[3] / "docs" / "PRIVACY_POLICY.md"
        assert "Anonymous usage counts" in md.read_text()
