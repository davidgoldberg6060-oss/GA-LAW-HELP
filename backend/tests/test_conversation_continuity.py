"""Hybrid continuity: each AI screen resumes its own thread; the AI also gets ONE short line about the
latest topic on another screen. Context-dependent answers never touch the question-keyed public cache."""
import os
import secrets
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="galawhelp-convo-"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp / 'convo.db'}")
os.environ.setdefault("EVIDENCE_DIR", str(_tmp / "evidence"))
os.environ.setdefault("JWT_SECRET", "unit-test-secret-that-is-longer-than-32-characters")

import pytest
from fastapi.testclient import TestClient

from app import anonymous_access, answer_cache, conversation_memory as convo, main
from app.grounded_legal_assistant import grounded_legal_response

ROOT = Path(__file__).resolve().parents[2]
CAR = "I was charged with possession after police searched my car without a warrant"
FIRST = "what motion should I file first?"


@pytest.fixture(autouse=True)
def _reset():
    anonymous_access.ai_counter.reset(); anonymous_access.anon_create_counter.reset(); answer_cache.clear()
    yield
    anonymous_access.ai_counter.reset(); anonymous_access.anon_create_counter.reset(); answer_cache.clear()


def _auth(client):
    r = client.post("/auth/anonymous", json={"device_key": secrets.token_urlsafe(32)}, headers={"X-Real-IP": "10.9.0." + str(secrets.randbelow(200))})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def _fake(calls):
    def fake(query, mode, ai, db=None, conversation=None):
        calls.append({"query": query, "mode": mode, "conversation": conversation})
        return {"analysis": f"Short answer\nAnswer {len(calls)} about: {query[-60:]}", "authorities": [], "laws_cited": [],
                "suggested_motions": [{"title": "Motion to suppress evidence"}] if "search" in query else []}
    return fake


# ---------- pure helpers ----------
def test_follow_up_detection_and_focus_from_other_screen():
    assert convo.is_follow_up(FIRST)
    assert convo.is_follow_up("can they use that against me?")
    assert not convo.is_follow_up(CAR)
    assert not convo.is_follow_up("how do I get my security deposit back from my landlord")
    other = {"feature": "ai_help", "feature_label": "AI Help", "user_text": CAR, "answer_summary": "x\nMotions it suggested: Motion to suppress evidence", "created_at": 1.0}
    ctx = {"thread": [], "elsewhere": other}
    focus = convo.focus_question(FIRST, ctx)
    assert focus.startswith(CAR) and focus.endswith(FIRST)
    # a self-contained new topic is retrieved alone
    assert convo.focus_question("how do I get my security deposit back", ctx) == "how do I get my security deposit back"


def test_elsewhere_note_is_one_bounded_line():
    long = {"feature": "charge_check", "feature_label": "Charge Check", "user_text": "x " * 500,
            "answer_summary": "Motions it suggested: " + "; ".join(["Motion to suppress evidence"] * 20), "created_at": 1.0}
    line = convo.elsewhere_line(long)
    assert "\n" not in line and len(line) <= convo.ELSEWHERE_MAX_CHARS and line.startswith("Last topic elsewhere in the app (Charge Check)")
    block = convo.context_block({"thread": [], "elsewhere": long})
    assert block == line  # no cross-screen transcript, only the note


def test_prompt_gets_own_thread_plus_note_and_motion_matching_uses_focus():
    prompts = []
    other = {"feature": "ai_help", "feature_label": "AI Help", "user_text": CAR, "answer_summary": "Short summary", "created_at": 1.0}
    r = grounded_legal_response(FIRST, "general", lambda p: prompts.append(p) or "Short answer\nFile a motion to suppress first.",
                                db=None, conversation={"thread": [], "elsewhere": other})
    assert "Last topic elsewhere in the app (AI Help): " + CAR in prompts[0]
    assert "This is a continuing conversation" in prompts[0]
    assert r["focus_question"].startswith(CAR)
    # Without context the prompt is unchanged (no continuity text).
    prompts.clear()
    grounded_legal_response(FIRST, "general", lambda p: prompts.append(p) or "Short answer\nok", db=None)
    assert "continuing conversation" not in prompts[0] and "elsewhere" not in prompts[0]


def test_motion_keys_follow_the_car_search_context():
    from app.defense_help import motion_keys
    assert motion_keys(FIRST) == []  # alone, the question names no topic
    focus = convo.focus_question(FIRST, {"thread": [], "elsewhere": {"feature_label": "AI Help", "user_text": CAR, "answer_summary": ""}})
    assert any("suppress" in k for k in motion_keys(focus))


# ---------- API ----------
def test_screen_threads_note_cache_bypass_and_start_fresh(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "grounded_legal_response", _fake(calls))
    with TestClient(main.app) as c:
        h = _auth(c)
        a = c.post("/public/rights-assistant", headers=h, json={"query": CAR, "mode": "general"}).json()
        assert calls[-1]["conversation"] is None and a["continuity"]["continued"] is False and a["continuity"]["turn_id"]
        # Motions screen (another feature endpoint): gets only the one-line note about AI Help
        m = c.post("/internal/legal-assistant", headers=h, json={"query": FIRST, "mode": "motions"}).json()
        ctx = calls[-1]["conversation"]
        assert ctx["thread"] == [] and ctx["elsewhere"]["user_text"] == CAR and ctx["elsewhere"]["feature"] == "ai_help"
        assert m["continuity"]["elsewhere_screen"] == "AI Help"
        # Back on AI Help: its own thread (1 turn); the newer Motions turn is the note
        c.post("/public/rights-assistant", headers=h, json={"query": "can they use that against me?", "mode": "general"})
        ctx = calls[-1]["conversation"]
        assert [t["user_text"] for t in ctx["thread"]] == [CAR] and ctx["elsewhere"]["feature"] == "motions"
        # GET shows per-screen state
        g = c.get("/me/conversation?feature=ai_help", headers=h).json()
        assert g["screen_last_topic"].startswith("can they use that") and len(g["turns"]) == 2
        # Start fresh on AI Help only; Motions keeps its thread
        assert c.delete("/me/conversation?feature=ai_help", headers=h).json()["cleared"] == 2
        assert c.get("/me/conversation?feature=ai_help", headers=h).json()["turns"] == []
        assert len(c.get("/me/conversation?feature=motions", headers=h).json()["turns"]) == 1
        assert c.delete("/me/conversation?feature=bogus", headers=h).status_code == 400
        # After Start fresh, AI Help no longer gets the note about the (older) Motions topic either
        c.post("/public/rights-assistant", headers=h, json={"query": "how do I get my security deposit back", "mode": "general"})
        assert calls[-1]["conversation"] is None
        # Forget everything
        c.delete("/me/conversation", headers=h)
        assert c.get("/me/conversation?feature=motions", headers=h).json()["turns"] == []


def test_context_answers_never_use_question_keyed_cache(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "grounded_legal_response", _fake(calls))
    with TestClient(main.app) as c:
        # A guest caches the bare follow-up question
        c.post("/public/rights-assistant", json={"query": FIRST, "mode": "general"})
        c.post("/public/rights-assistant", json={"query": FIRST, "mode": "general"})
        assert len(calls) == 1  # guest repeat served from cache
        h = _auth(c)
        c.post("/public/rights-assistant", headers=h, json={"query": CAR, "mode": "general"})  # creates context
        n = len(calls)
        r = c.post("/public/rights-assistant", headers=h, json={"query": FIRST, "mode": "general"}).json()
        assert len(calls) == n + 1 and not r.get("cached")  # cache bypassed because context exists
        # and the context answer was not written to the cache for guests
        g = c.post("/public/rights-assistant", json={"query": FIRST, "mode": "general"}).json()
        assert "Answer 1 about" in g["analysis"]


def test_use_context_false_and_remember_false(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "grounded_legal_response", _fake(calls))
    with TestClient(main.app) as c:
        h = _auth(c)
        q1, q2 = CAR + " " + secrets.token_hex(4), FIRST + " " + secrets.token_hex(4)  # not in the shared cache
        c.post("/public/rights-assistant", headers=h, json={"query": q1, "mode": "general"})
        c.post("/public/rights-assistant", headers=h, json={"query": q2, "mode": "general", "use_context": False, "remember": False})
        assert len(calls) == 2 and calls[-1]["conversation"] is None
        assert len(c.get("/me/conversation?feature=ai_help", headers=h).json()["turns"]) == 1


def test_bad_token_on_guest_route_is_ignored_and_rights_route_stays_ip_capped(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "grounded_legal_response", _fake(calls))
    with TestClient(main.app) as c:
        r = c.post("/public/rights-assistant", headers={"Authorization": "Bearer nope"}, json={"query": CAR, "mode": "general"})
        assert r.status_code == 200 and "continuity" not in r.json()
    assert anonymous_access._IP_ONLY_PATHS[0].match("/public/rights-assistant")


def test_charge_check_receives_note(monkeypatch):
    seen = {}
    monkeypatch.setattr(main, "grounded_legal_response", _fake([]))
    def fake_cc(situation, ask, db=None, case_summary=None, conversation=None):
        seen["ctx"] = conversation
        return {"situation": situation, "charges": [{"charge": "Possession"}], "message": None}
    monkeypatch.setattr(main, "analyze_charge_check", fake_cc)
    with TestClient(main.app) as c:
        h = _auth(c)
        c.post("/public/rights-assistant", headers=h, json={"query": CAR, "mode": "general"})
        r = c.post("/charge-check", headers=h, json={"situation": "what could I be charged with for that?", "save_case": False}).json()
        assert seen["ctx"]["elsewhere"]["user_text"] == CAR and r["continuity"]["continued"]


def test_account_deletion_removes_conversation(monkeypatch):
    monkeypatch.setattr(main, "grounded_legal_response", _fake([]))
    with TestClient(main.app) as c:
        key = secrets.token_urlsafe(32)
        tok = c.post("/auth/anonymous", json={"device_key": key}, headers={"X-Real-IP": "10.8.0.1"}).json()
        h = {"Authorization": "Bearer " + tok["access_token"]}
        c.post("/public/rights-assistant", headers=h, json={"query": CAR, "mode": "general"})
        from app.database import SessionLocal
        db = SessionLocal()
        assert convo.recent(db, tok["user"]["id"])
        assert c.post("/me/delete", headers=h, json={"password": key, "confirm": "DELETE"}).status_code == 200
        assert convo.recent(db, tok["user"]["id"]) == []
        db.close()


def test_elsewhere_names_the_topic_a_bare_follow_up_was_about(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "grounded_legal_response", _fake(calls))
    with TestClient(main.app) as c:
        h = _auth(c)
        c.post("/public/rights-assistant", headers=h, json={"query": CAR, "mode": "general"})
        c.post("/public/rights-assistant", headers=h, json={"query": FIRST, "mode": "general"})
        g = c.get("/me/conversation?feature=charge_check", headers=h).json()
        assert g["elsewhere_topic"].startswith("I was charged with possession") and g["elsewhere_screen"] == "AI Help"
