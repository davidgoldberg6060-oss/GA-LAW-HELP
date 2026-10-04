"""Guest free research must survive questions longer than the encounter query cap.

This does not claim corpus coverage or that any citation is current Georgia law.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_guest_clients_clip_encounter_situation_and_rights_matches_internal_limit():
    guest = (ROOT / "src" / "guestPublic.ts").read_text(encoding="utf-8")
    android = (ROOT / "android/app/src/main/java/help/galaw/standalone/GuestPublicApi.kt").read_text(encoding="utf-8")
    main = (ROOT / "backend/app/main.py").read_text(encoding="utf-8")
    public = main.split("def public_rights_assistant", 1)[1].split("for _route in list", 1)[0]
    assert "encounterSituation(q)" in guest
    assert "ENCOUNTER_SITUATION_MAX = 400" in guest
    assert "/public/rights-assistant" in guest
    assert "/public/encounter" in guest
    assert "Authorization" not in guest
    assert "situation.trim().take(ENCOUNTER_SITUATION_MAX)" in android
    assert "ENCOUNTER_SITUATION_MAX = 400" in android
    assert 'post(baseUrl, "/public/rights-assistant"' in android
    assert "len(query)>12000" in public
    assert "len(query)>4000" not in public
    assert "login_required" in public
