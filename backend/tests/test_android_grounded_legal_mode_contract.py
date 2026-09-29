from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODE = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedLegalMode.kt"


def _source() -> str:
    return MODE.read_text(encoding="utf-8")


def test_all_native_legal_ai_modes_use_dedicated_grounded_calls():
    source = _source()
    expected = {
        'CASE_ANALYSIS("case_analysis")': "api.caseAnalysisWithVerifiedAuthorities(clean)",
        'RIGHTS("rights")': "api.rightsAnalysis(clean)",
        'MOTIONS("motions")': "api.motionsAnalysis(clean)",
        'TALK_TO_ME("talk_to_me")': "api.talkToMeAnalysis(clean)",
    }
    for mode, call in expected.items():
        assert mode in source
        assert call in source
    assert "publicAsk(" not in source


def test_native_mode_adapter_preserves_backend_authority_rendering():
    source = _source()
    assert "GroundedLegalResult.answer(raw)" in source
    assert "GroundedLegalResult.authoritySummary(raw)" in source
    assert "authoritySummary" in source
    assert "displayText" in source


def test_native_mode_adapter_rejects_empty_and_unbounded_requests():
    source = _source()
    assert 'require(clean.isNotEmpty())' in source
    assert 'require(clean.length <= 50_000)' in source
