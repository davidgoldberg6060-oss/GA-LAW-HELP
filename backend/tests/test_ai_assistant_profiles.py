from app.ai_assistant import _is_complex_legal_request, _request_profile


def test_motion_screen_uses_deeper_reasoning_profile(monkeypatch):
    monkeypatch.delenv("OPENAI_LEGAL_REASONING_EFFORT", raising=False)
    profile = _request_profile("GEORGIA CRIMINAL CASE MOTION SCREEN\nVERIFIED MOTION REGISTRY:\nMotion for new trial")
    assert profile["reasoning"]["effort"] == "medium"
    assert profile["max_output_tokens"] == 2200
    assert profile["timeout"] == 55.0


def test_simple_question_stays_on_fast_profile(monkeypatch):
    monkeypatch.delenv("OPENAI_FAST_REASONING_EFFORT", raising=False)
    profile = _request_profile("What does arraignment mean?")
    assert profile["reasoning"]["effort"] == "none"
    assert profile["max_output_tokens"] == 900
    assert profile["timeout"] == 30.0


def test_long_legal_context_is_complex():
    assert _is_complex_legal_request("case facts " + ("x" * 2600))


def test_profile_settings_are_environment_tunable(monkeypatch):
    monkeypatch.setenv("OPENAI_LEGAL_REASONING_EFFORT", "high")
    monkeypatch.setenv("OPENAI_LEGAL_MAX_OUTPUT_TOKENS", "3000")
    monkeypatch.setenv("OPENAI_LEGAL_TIMEOUT_SECONDS", "60")
    profile = _request_profile("habeas corpus Georgia")
    assert profile["reasoning"]["effort"] == "high"
    assert profile["max_output_tokens"] == 3000
    assert profile["timeout"] == 60.0
