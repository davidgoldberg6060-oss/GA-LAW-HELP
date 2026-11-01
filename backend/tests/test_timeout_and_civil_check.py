"""1.6.0: Talk to Me routing, fast model, answer cache, Android timeout handling, Civil Case Check."""
import json
from pathlib import Path

from app import ai_assistant, answer_cache
from app.civil_check_service import analyze_civil_check, validate_civil_check, civil_check_note_text
from app.civil_topics import topic_sections, follow_ups
from app.grounded_legal_assistant import SUPPORTED_MODES, grounded_legal_response

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "android/app/src/main/java/help/galaw/standalone"


def _hit(section, text, status="verified"):
    return {"title": f"Section {section}", "citation": f"O.C.G.A. § {section}", "source_url": f"https://law.example.gov/{section}",
            "verification_status": status, "excerpt": text, "full_text": text, "record_type": "statute",
            "currency_status": "current", "precedential_status": "unknown", "negative_treatment": []}


# ---------- routing / speed ----------
def test_talk_to_me_uses_general_mode_and_rights_stays_rights():
    mode = (SRC / "GroundedLegalMode.kt").read_text()
    assert 'Mode.TALK_TO_ME -> GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, clean, "general")' in mode
    assert 'Mode.RIGHTS -> GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, clean, "rights")' in mode
    assert "GuestPublicApi.encounter" not in (SRC / "TalkToMeController.kt").read_text()
    assert "general" in SUPPORTED_MODES


def test_general_mode_prompt_is_not_police_encounter():
    seen = {}
    def ai(prompt):
        seen["p"] = prompt
        return "SHORT ANSWER\nYes.\nHOW IT WORKS IN GEORGIA\nRecord restriction."
    r = grounded_legal_response("how can I get a felony expunged on my record", "general", ai)
    assert "SHORT ANSWER" in seen["p"] and "NOT a police encounter" in seen["p"]
    assert "WHAT LAW ENFORCEMENT MAY" not in seen["p"]
    assert r["sections"]["short_answer"] == "Yes."


def test_expungement_maps_to_record_restriction():
    assert "35-3-37" in topic_sections("how can I get a felony expunged on my record")
    assert "44-7-34" in topic_sections("my landlord won't return my security deposit")


def test_fast_profile_uses_lite_model_even_for_complex_markers(monkeypatch):
    monkeypatch.delenv("GEMINI_FAST_MODEL", raising=False)
    p = ai_assistant._gemini_profile("appeals sentencing post-conviction", "gemini-3.5-flash", "fast")
    assert p["model"] == "gemini-3.5-flash-lite" and p["max_output_tokens"] <= 2400 and p["timeout"] <= 20
    q = ai_assistant._gemini_profile("appeals sentencing", "gemini-3.5-flash")
    assert q["model"] == "gemini-3.5-flash"  # quality path unchanged


def test_public_route_uses_fast_model_and_cache():
    main = (ROOT / "backend/app/main.py").read_text()
    route = main[main.index("@app.post('/public/rights-assistant')"):]
    route = route[:route.index("@app.", 5)]
    assert "ask_fast" in route and "answer_cache.get(query,mode,db=db)" in route and "answer_cache.put" in route
    chat = main[main.index("@app.post('/cases/{case_id}/chat')"):][:1500]
    assert "answer_cache" not in chat  # per-user case chat is never cached


def test_answer_cache_normalizes_and_expires():
    answer_cache.clear()
    answer_cache.put("How do I get  divorced?", "general", {"answer": "x"}, now=1000)
    assert answer_cache.get("how do i get divorced", "general", now=1001)["answer"] == "x"
    assert answer_cache.get("how do i get divorced", "rights", now=1001) is None
    assert answer_cache.get("how do i get divorced", "general", now=1000 + answer_cache.TTL_SECONDS + 1) is None


def test_public_endpoint_returns_follow_ups_and_help(monkeypatch):
    from fastapi.testclient import TestClient
    from app import main
    answer_cache.clear()
    calls = []
    monkeypatch.setattr(main, "grounded_legal_response", lambda q, m, ai, db=None: calls.append(m) or {"analysis": "ok answer", "authorities": []})
    c = TestClient(main.app)
    body = {"query": "my landlord won't return my security deposit", "mode": "general"}
    r1 = c.post("/public/rights-assistant", json=body).json()
    r2 = c.post("/public/rights-assistant", json=body).json()
    assert calls == ["general"] and r2.get("cached") is True
    assert len(r1["follow_ups"]) >= 2 and any("glsp.org" in h["url"] for h in r1["help_links"])


# ---------- Android timeout handling ----------
def test_android_ai_timeouts_and_friendly_retry():
    guest = (SRC / "GuestPublicApi.kt").read_text()
    assert "AI_READ_TIMEOUT_MS = 60_000" in guest and 'open(baseUrl, path, "POST", AI_READ_TIMEOUT_MS)' in guest
    assert "ApiNetworkException(if (AiErrors.isTimeout(e))" in guest
    api = (SRC / "ApiClient.kt").read_text()
    assert "AI_READ_MS = 60_000" in api and api.count("readMs=AI_READ_MS") >= 2
    errors = (SRC / "AiErrors.kt").read_text()
    assert 'it == "timeout"' in errors and "tap Retry" in errors
    home = (SRC / "HomeActivity.kt").read_text()
    assert "AiErrors.message(e)" in home and "c.retry{" in home and "c.progress()" in home
    assert 'e.message?:"Something went wrong. Please try again.",now(),inContext=false' not in home


def test_android_chats_persist_and_delete_wipes_saved_copy():
    store = (SRC / "ChatStore.kt").read_text()
    assert "prefs.remove(key)" in store
    t = (SRC / "ChatTranscript.kt").read_text()
    assert "fun clear() { items.clear(); onChange?.invoke(this) }" in t
    home = (SRC / "HomeActivity.kt").read_text()
    assert "ChatStore.open(this, ChatStore.TALK_KEY)" in home and "ChatStore.caseKey(caseId)" in home


# ---------- Civil Case Check ----------
DEPOSIT = ("Within one month after the termination of the residential lease or the surrender and acceptance of the "
           "premises, whichever occurs last, a landlord shall return to the tenant the full security deposit.")
MAGISTRATE = "Magistrate courts have jurisdiction to try civil claims where the amount demanded does not exceed $15,000.00."


def _ai_factory(analysis):
    def ai(prompt):
        if "Return ONLY JSON: {\"sections\"" in prompt:
            return json.dumps({"sections": ["44-7-34", "99-9-999"]})
        return json.dumps(analysis)
    return ai


def _lookup(sections):
    db = {"44-7-34": _hit("44-7-34", DEPOSIT), "15-10-2": _hit("15-10-2", MAGISTRATE)}
    return [db[s] for s in sections if s in db]


def test_civil_check_keeps_only_verified_and_quoted_items():
    analysis = {
        "claims": [{"side": "you", "claim": "Return of security deposit", "citation": "O.C.G.A. § 44-7-34", "why": "Lease ended."},
                   {"side": "you", "claim": "Invented", "citation": "O.C.G.A. § 99-9-999", "why": "x"}],
        "court": {"court": "magistrate", "why": "Small amount.", "citation": "O.C.G.A. § 15-10-2", "limit_quote": "does not exceed $15,000.00"},
        "deadlines": [{"title": "Return deadline", "quote": "Within one month after the termination of the residential lease", "citation": "O.C.G.A. § 44-7-34"},
                      {"title": "Made up", "quote": "within 3 days", "citation": "O.C.G.A. § 44-7-34"}],
        "evidence": ["Lease", "Move-out photos", "Hide the money from the landlord"],
        "weak_spots": [{"side": "other_side", "title": "Damage", "explanation": "Landlord may claim damage.", "citations": ["O.C.G.A. § 44-7-34"]}],
        "low_cost_paths": [{"title": "Demand letter", "explanation": "Send a written demand.", "citations": []},
                           {"title": "Hide assets", "explanation": "Transfer your assets before judgment.", "citations": []}],
        "lawyer_take": {"text": "Send a demand letter and keep your photos. If needed file in magistrate court.", "citations": ["O.C.G.A. § 44-7-34"]},
    }
    r = analyze_civil_check("my landlord won't return my security deposit", _ai_factory(analysis), lookup=_lookup)
    assert [c["claim"] for c in r["claims"]] == ["Return of security deposit"]
    assert r["court"]["court"] == "magistrate" and r["court"]["limit"] == "does not exceed $15,000.00"
    assert [d["title"] for d in r["deadlines"]] == ["Return deadline"]
    assert [p["title"] for p in r["low_cost_paths"]] == ["Demand letter"]
    assert r["dropped_items"] >= 3 and r["lawyer_take"]
    assert any("glsp.org" in h["url"] for h in r["help_resources"])
    assert "CIVIL CASE CHECK" in civil_check_note_text(r)


def test_civil_check_unquoted_dollar_limit_is_dropped():
    kept, _ = validate_civil_check({"court": {"court": "magistrate", "citation": "O.C.G.A. § 15-10-2", "limit_quote": "up to $50,000"}},
                                   [_hit("15-10-2", MAGISTRATE)])
    assert kept["court"]["limit"] is None


def test_civil_check_refuses_hiding_assets():
    r = analyze_civil_check("how do I hide my money from my wife before the divorce", lambda p: "{}", lookup=_lookup)
    assert r["refused"] and not r["claims"]


def test_civil_check_endpoint_creates_civil_case(monkeypatch):
    main = (ROOT / "backend/app/main.py").read_text()
    assert "@app.post('/civil-check')" in main and "case_type='civil'" in main
    assert "@app.post('/cases/{case_id}/civil-check')" in main
    from app.anonymous_access import is_ai_path
    assert is_ai_path("POST", "/civil-check") and is_ai_path("POST", "/cases/3/civil-check")


def test_android_civil_check_reachable_from_drawer_and_case():
    home = (SRC / "HomeActivity.kt").read_text()
    assert '"civil"->showCivilCheck(null,null)' in home and "showCivilCheck(caseId," in home
    assert 'text="Civil"' in home and "caseType" in home
    assert 'HomeDrawerItem("civil", "Civil Case Check", false)' in (SRC / "HomeDrawerCatalog.kt").read_text()
    assert "/civil-check" in (SRC / "ApiClient.kt").read_text()


def test_follow_ups_are_topic_specific():
    assert any("deposit" in q.lower() for q in follow_ups("security deposit"))
    assert len(follow_ups("something else")) == 3
