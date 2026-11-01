from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODE = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedLegalMode.kt"
GUEST = ROOT / "android/app/src/main/java/help/galaw/standalone/GuestPublicApi.kt"
BACKEND_MAIN = ROOT / "backend/app/main.py"


def _source() -> str:
    return MODE.read_text(encoding="utf-8")


def test_all_native_legal_ai_modes_use_dedicated_grounded_calls():
    """Private modes use login-only /internal/legal-assistant. Rights and Talk to Me were
    deliberately moved (commit 4a2ad5f, docs/GUEST_PUBLIC_RIGHTS.md) to the guest
    POST /public/rights-assistant endpoint, which runs the same grounded_legal_response
    pipeline (verified authorities only, no invented citations). Neither may use the
    ungrounded publicAsk path.
    """
    source = _source()
    expected = {
        'CASE_ANALYSIS("case_analysis")': "Mode.CASE_ANALYSIS -> api.caseAnalysisWithVerifiedAuthorities(clean)",
        'RIGHTS("rights")': 'Mode.RIGHTS -> GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, clean, "rights")',
        'MOTIONS("motions")': "Mode.MOTIONS -> api.motionsAnalysis(clean)",
        'TALK_TO_ME("talk_to_me")': 'Mode.TALK_TO_ME -> GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, clean, "general")',
    }
    for mode, call in expected.items():
        assert mode in source
        assert call in source
    assert "publicAsk(" not in source


def test_guest_rights_modes_hit_the_grounded_public_endpoint():
    guest = GUEST.read_text(encoding="utf-8")
    assert 'post(baseUrl, "/public/rights-assistant", body)' in guest
    assert 'put("mode", mode)' in guest
    backend = BACKEND_MAIN.read_text(encoding="utf-8")
    start = backend.index("@app.post('/public/rights-assistant')")
    end = backend.index("@app.", start + 1)
    route = backend[start:end]
    assert "grounded_legal_response(query, mode, ask_fast, db=db)" in route
    assert "if mode not in PUBLIC_ASSISTANT_MODES" in route
    assert "PUBLIC_ASSISTANT_MODES={'rights','talk_to_me','general'}" in backend
    fallback_start = backend.index("def _guest_rights_without_corpus")
    fallback = backend[fallback_start:start]
    assert "'authorities': []" in fallback
    assert "'grounded_authority_count': 0" in fallback


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
