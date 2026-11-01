"""Deleting AI chat messages.

Case Chat and Talk to Me transcripts are kept only on the phone; the server stores no chat
messages. The server only ever sees the history the app sends with each question, so a message
the user deleted on the phone is never sent to the AI again. Saved results that DO live on the
server (Charge Check results saved as case notes) are hard-deleted by their owner only.
"""
import os
import secrets
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="galawhelp-msgdel-"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp / 'msgdel.db'}")
os.environ.setdefault("EVIDENCE_DIR", str(_tmp / "evidence"))
os.environ.setdefault("JWT_SECRET", "unit-test-secret-that-is-longer-than-32-characters")

import pytest
from fastapi.testclient import TestClient

from app import anonymous_access, main, models
from app.case_chat_service import build_case_chat_request, parse_history
from app.database import SessionLocal
from app.main import app

ROOT = Path(__file__).resolve().parents[3]
KOTLIN = ROOT / "android/app/src/main/java/help/galaw/standalone"


@pytest.fixture(autouse=True)
def _reset_limits():
    anonymous_access.ai_counter.reset(); anonymous_access.anon_create_counter.reset()
    yield
    anonymous_access.ai_counter.reset(); anonymous_access.anon_create_counter.reset()


def _auth(client):
    r = client.post("/auth/anonymous", json={"device_key": secrets.token_urlsafe(32)}, headers={"X-Real-IP": "10.1.2.3"})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def _case(client, h):
    r = client.post("/cases", headers=h, json={"title": "Traffic stop", "narrative": "Pulled over"})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_deleted_messages_are_not_sent_to_ai_and_chat_is_owner_only(monkeypatch):
    seen = []

    def fake_analyze(*, user_message, history, case_summary, ask_ai, db):
        seen.append([(m.role, m.content) for m in history])
        return {"answer": "ok", "authorities": []}

    monkeypatch.setattr(main, "analyze_case_conversation", fake_analyze)
    with TestClient(app) as client:
        a, b = _auth(client), _auth(client)
        cid = _case(client, a)
        # The phone deleted the first question/answer pair; only the remaining turn is sent.
        kept = [{"role": "user", "content": "keep this"}, {"role": "assistant", "content": "kept answer"}]
        r = client.post(f"/cases/{cid}/chat", headers=a, json={"message": "next", "history": kept})
        assert r.status_code == 200, r.text
        assert seen[-1] == [("user", "keep this"), ("assistant", "kept answer")]
        # Cleared chat: no history at all reaches the AI.
        assert client.post(f"/cases/{cid}/chat", headers=a, json={"message": "fresh", "history": []}).status_code == 200
        assert seen[-1] == []
        # Another device cannot use this case's chat.
        assert client.post(f"/cases/{cid}/chat", headers=b, json={"message": "x", "history": []}).status_code == 404
        assert len(seen) == 2


def test_server_stores_no_chat_messages():
    tables = set(models.Base.metadata.tables)
    assert not any("chat" in t or "message" in t for t in tables), tables


def test_case_chat_request_only_contains_supplied_history():
    request = build_case_chat_request(user_message="q", history=parse_history([{"role": "user", "content": "still here"}]), case_summary="Case title: X")
    assert "still here" in request and "deleted secret" not in request


def test_saved_charge_check_note_is_hard_deleted_by_owner_only():
    with TestClient(app) as client:
        a, b = _auth(client), _auth(client)
        cid = _case(client, a)
        owner_id = client.get("/me", headers=a).json()["id"]
        nid = 987654
        with SessionLocal() as db:  # explicit id: SQLite cannot autoincrement the BigInteger key
            db.add(models.CaseNote(id=nid, case_id=cid, owner_id=owner_id, note_type="CHARGE_CHECK", title="Charge Check", content="result", language="en")); db.commit()
        assert client.delete(f"/cases/{cid}/notes/{nid}", headers=b).status_code == 404
        assert client.delete(f"/cases/{cid}/notes/{nid}", headers=a).json() == {"deleted": True}
        with SessionLocal() as db:
            assert db.get(models.CaseNote, nid) is None
        assert client.delete(f"/cases/{cid}/notes/{nid}", headers=a).status_code == 404


def test_android_chats_offer_copy_share_delete_and_clear_with_confirmation():
    home = (KOTLIN / "HomeActivity.kt").read_text(encoding="utf-8")
    screens = (KOTLIN / "GaScreens.kt").read_text(encoding="utf-8")
    transcript = (KOTLIN / "ChatTranscript.kt").read_text(encoding="utf-8")
    assert 'arrayOf("Copy","Share","Delete")' in home
    assert "Delete this message?" in home and "Clear this chat?" in home
    assert home.count("wireChatDelete(c,") == 2  # Talk to Me and Case Chat
    assert "talk.transcript()" in home and "t.roleHistory(20)" in home  # AI context rebuilt after deletes
    assert "setOnLongClickListener" in screens and '"Clear chat"' in screens
    assert "fun delete(id: Long)" in transcript and "fun clear()" in transcript
