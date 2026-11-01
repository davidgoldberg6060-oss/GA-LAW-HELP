import io
import json
import urllib.error

import pytest

from app import ai_assistant

KEYS = ("AI_PROVIDER", "GEMINI_API_KEY", "XAI_API_KEY", "OPENAI_API_KEY", "GEMINI_MODEL", "GEMINI_FAST_MODEL")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in KEYS:
        monkeypatch.delenv(key, raising=False)


class FakeResponse:
    def __init__(self, body):
        self.body = json.dumps(body).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _http_error(url, status):
    return urllib.error.HTTPError(url, status, "err", {}, io.BytesIO(b'{"error":{"code":%d,"status":"RESOURCE_EXHAUSTED"}}' % status))


def test_gemini_preferred_when_key_set(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    monkeypatch.setenv("OPENAI_API_KEY", "o-test")
    assert [p["name"] for p in ai_assistant._providers()] == ["gemini", "openai"]
    assert ai_assistant._provider()["default_model"] == "gemini-3.5-flash"


def test_ai_provider_env_overrides_order(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    monkeypatch.setenv("OPENAI_API_KEY", "o-test")
    monkeypatch.setenv("AI_PROVIDER", "openai")
    assert [p["name"] for p in ai_assistant._providers()] == ["openai", "gemini"]


def test_xai_still_works_without_gemini(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "x-test")
    monkeypatch.setenv("OPENAI_API_KEY", "o-test")
    assert ai_assistant._provider()["name"] == "xai"


def test_no_keys_raises(monkeypatch):
    with pytest.raises(RuntimeError, match="not configured"):
        ai_assistant.ask_openai("hi")


def test_gemini_request_shape_and_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    monkeypatch.setenv("GEMINI_FAST_MODEL", "gemini-test")
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["headers"] = {k.lower(): v for k, v in request.header_items()}
        seen["body"] = json.loads(request.data)
        return FakeResponse({"candidates": [{"content": {"parts": [{"text": "thinking", "thought": True}, {"text": "Answer "}, {"text": "text"}]}}]})

    monkeypatch.setattr(ai_assistant.urllib.request, "urlopen", fake_urlopen)
    assert ai_assistant.ask_openai("Return only JSON about search") == "Answer text"
    assert seen["url"].endswith("/models/gemini-test:generateContent")
    assert seen["headers"]["x-goog-api-key"] == "g-test"
    assert "authorization" not in seen["headers"]
    assert seen["body"]["contents"][0]["parts"][0]["text"] == "Return only JSON about search"
    assert seen["body"]["systemInstruction"]["parts"][0]["text"] == ai_assistant.SYSTEM_INSTRUCTIONS
    assert seen["body"]["generationConfig"]["responseMimeType"] == "application/json"
    assert seen["body"]["generationConfig"]["thinkingConfig"]["thinkingLevel"] == "low"


def test_gemini_empty_response_raises(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    monkeypatch.setattr(ai_assistant.urllib.request, "urlopen", lambda r, timeout: FakeResponse({"candidates": [{"finishReason": "SAFETY"}]}))
    with pytest.raises(RuntimeError, match="unavailable"):
        ai_assistant.ask_openai("hi")


def test_gemini_429_falls_back_to_openai(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    monkeypatch.setenv("OPENAI_API_KEY", "o-test")
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        if "generativelanguage" in request.full_url:
            raise _http_error(request.full_url, 429)
        return FakeResponse({"output_text": "openai answer"})

    monkeypatch.setattr(ai_assistant.urllib.request, "urlopen", fake_urlopen)
    assert ai_assistant.ask_openai("hi") == "openai answer"
    assert calls[-1].endswith('/responses') and len(calls) >= 2  # 429 rotates the Gemini chain, then OpenAI


def test_gemini_429_without_fallback_raises_runtime_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")

    def fake_urlopen(request, timeout):
        raise _http_error(request.full_url, 429)

    monkeypatch.setattr(ai_assistant.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError):
        ai_assistant.ask_openai("hi")


def test_non_quota_error_does_not_fall_back(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    monkeypatch.setenv("OPENAI_API_KEY", "o-test")
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(1)
        raise _http_error(request.full_url, 400)

    monkeypatch.setattr(ai_assistant.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError):
        ai_assistant.ask_openai("hi")
    assert len(calls) == 1
