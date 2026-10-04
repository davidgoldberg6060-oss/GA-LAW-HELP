"""Clients must respect the guest endpoint length limits instead of failing with 400/422.

- POST /public/rights-assistant rejects `query` over 4000 characters.
- GET /public/encounter rejects `situation` over 400 characters (FastAPI max_length).
Android Talk to Me / guest rights and the web Free research flow must stay within those limits
(trim the supplementary encounter label, budget conversation history, and show a clear message
when the user's own question is too long).
"""
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
KT = ROOT / "android/app/src/main/java/help/galaw/standalone"
MAIN = ROOT / "backend/app/main.py"
PUBLIC_RIGHTS = ROOT / "backend/app/public_rights.py"
GUEST_TS = ROOT / "src/guestPublic.ts"


def _server_query_limit() -> int:
    main = MAIN.read_text(encoding="utf-8")
    route = main.split("@app.post('/public/rights-assistant')", 1)[1].split("@app.", 1)[0]
    return int(re.search(r"if len\(query\)>(\d+)", route).group(1))


def _server_situation_limit() -> int:
    rights = PUBLIC_RIGHTS.read_text(encoding="utf-8")
    block = rights.split('@router.get("/encounter")', 1)[1].split("@router.", 1)[0]
    return int(re.search(r"max_length=(\d+)", block).group(1))


def _kt_const(name: str) -> int:
    source = (KT / "GuestPublicApi.kt").read_text(encoding="utf-8")
    return int(re.search(rf"const val {name} = ([\d_]+)", source).group(1).replace("_", ""))


def _ts_const(name: str) -> int:
    source = GUEST_TS.read_text(encoding="utf-8")
    return int(re.search(rf"export const {name} = (\d+);", source).group(1))


def test_client_limits_match_server_limits():
    assert _server_query_limit() == 4000
    assert _server_situation_limit() == 400
    assert _kt_const("MAX_QUERY_CHARS") == _server_query_limit()
    assert _kt_const("MAX_SITUATION_CHARS") == _server_situation_limit()
    assert _ts_const("GUEST_QUERY_MAX_CHARS") == _server_query_limit()
    assert _ts_const("ENCOUNTER_SITUATION_MAX_CHARS") == _server_situation_limit()


def test_android_guest_api_trims_situation_and_rejects_overlong_query_clearly():
    source = (KT / "GuestPublicApi.kt").read_text(encoding="utf-8")
    assert "situation.trim().take(MAX_SITUATION_CHARS)" in source
    assert 'URLEncoder.encode(encounterSituation(situation), "UTF-8")' in source
    assert "require(query.trim().length <= MAX_QUERY_CHARS) { QUERY_TOO_LONG_MESSAGE }" in source
    assert "shorten it to 4,000 characters" in source
    mode = (KT / "GroundedLegalMode.kt").read_text(encoding="utf-8")
    assert "if (mode == Mode.RIGHTS || mode == Mode.TALK_TO_ME)" in mode
    assert "require(clean.length <= GuestPublicApi.MAX_QUERY_CHARS) { GuestPublicApi.QUERY_TOO_LONG_MESSAGE }" in mode


def test_android_talk_to_me_budgets_history_to_the_guest_limit():
    for name in ("GroundedConversation.kt", "TalkToMeScreenModel.kt"):
        source = (KT / name).read_text(encoding="utf-8")
        assert "MAX_REQUEST_CHARS = GuestPublicApi.MAX_QUERY_CHARS" in source, name
        assert "require(fixedChars <= MAX_REQUEST_CHARS)" in source, name
        assert "Your message is too long for Talk to Me" in source, name
        assert "minOf(MAX_CONTEXT_CHARS, MAX_REQUEST_CHARS - fixedChars - CONTEXT_HEADER.length" in source, name
        assert ".takeLast(contextBudget)" in source, name


def test_web_free_research_trims_encounter_and_survives_its_failure():
    source = GUEST_TS.read_text(encoding="utf-8")
    assert "query.trim().slice(0, ENCOUNTER_SITUATION_MAX_CHARS)" in source
    assert "encodeURIComponent(encounterSituation(q))" in source
    assert "encodeURIComponent(q))" not in source
    assert "if (q.length > GUEST_QUERY_MAX_CHARS) throw new Error(GUEST_QUERY_TOO_LONG_MESSAGE);" in source
    assert ".catch(\n      (): PublicEncounterResponse => ({}),\n    )" in source


def test_server_enforces_the_limits_the_clients_rely_on():
    with TestClient(app) as client:
        ok = client.get("/public/encounter", params={"situation": "s" * 400})
        assert ok.status_code == 200
        too_long = client.get("/public/encounter", params={"situation": "s" * 401})
        assert too_long.status_code == 422
        rejected = client.post("/public/rights-assistant", json={"query": "q" * 4001, "mode": "talk_to_me"})
        assert rejected.status_code == 400
