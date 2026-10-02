from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODE = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedLegalMode.kt"


def _source() -> str:
    return MODE.read_text(encoding="utf-8")


def test_guest_rights_and_talk_use_public_endpoints_without_login():
    source = _source()
    assert 'RIGHTS("rights")' in source
    assert 'TALK_TO_ME("talk_to_me")' in source
    assert "guestRightsAndEncounter(clean, \"rights\")" in source
    assert "guestRightsAndEncounter(clean, \"talk_to_me\")" in source
    assert "GuestPublicApi.encounter(BuildConfig.API_BASE_URL, query)" in source
    assert "GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, query, mode)" in source
    assert "login_required", false" in source
    assert "api.rightsAnalysis(" not in source
    assert "api.talkToMeAnalysis(" not in source
    assert "publicAsk(" not in source


def test_private_case_and_motion_modes_stay_login_only():
    source = _source()
    assert 'CASE_ANALYSIS("case_analysis")' in source
    assert "api.caseAnalysisWithVerifiedAuthorities(clean)" in source
    assert 'MOTIONS("motions")' in source
    assert "api.motionsAnalysis(clean)" in source


def test_native_mode_adapter_preserves_backend_authority_rendering():
    source = _source()
    assert "GroundedLegalResult.answer(raw)" in source
    assert "GroundedLegalResult.authoritySummary(raw)" in source
    assert "authoritySummary" in source
    assert "displayText" in source


def test_native_mode_adapter_rejects_empty_and_unbounded_requests():
    source = _source()
    assert "require(clean.isNotEmpty())" in source
    assert "require(clean.length <= 50_000)" in source
