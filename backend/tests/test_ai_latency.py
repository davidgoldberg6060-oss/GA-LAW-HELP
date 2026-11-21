"""Nov 21: answers took 38-70 s (slow Gemini timeouts one after another, then a second full call for a plan retry).
The chain now has one budget, caps each call by the time left, and hedges chat answers with a parallel model."""
import time

import pytest

from app import ai_assistant as ai
from app import ai_models


@pytest.fixture(autouse=True)
def clean_cooldowns():
    ai_models._cooldowns.clear()
    yield
    ai_models._cooldowns.clear()


def slow(seconds, text="slow answer"):
    def call(timeout):
        time.sleep(min(seconds, timeout))
        if seconds > timeout:
            raise RuntimeError("AI provider timed out")
        return text
    return call


def test_hedge_starts_a_second_model_when_the_first_is_slow():
    started = time.monotonic()
    key, text = ai._run_chain([("a", slow(5)), ("b", slow(0.1, "fast answer"))], started + 10, 5, 0.3, 2)
    assert (key, text) == ("b", "fast answer") and time.monotonic() - started < 1.5


def test_failed_model_moves_on_immediately_and_deadline_is_respected():
    def boom(timeout):
        raise RuntimeError("AI provider is temporarily unreachable")
    started = time.monotonic()
    key, text = ai._run_chain([("a", boom), ("b", slow(0.05, "ok"))], started + 5, 5, None, 1)
    assert key == "b" and time.monotonic() - started < 1
    started = time.monotonic()
    key, _ = ai._run_chain([("a", slow(30)), ("b", slow(30))], started + 5, 30, None, 1)
    assert key is None and time.monotonic() - started < 5.5  # never past the deadline


def test_each_call_is_capped_by_the_time_left():
    seen = []

    def record(timeout):
        seen.append(timeout)
        return "x"
    ai._run_chain([("a", record)], time.monotonic() + 6, 15, None, 1)
    assert seen and seen[0] <= 6


def test_cooling_models_are_skipped():
    ai_models.mark_cooldown("a", 60, "test")
    key, _ = ai._run_chain([("a", slow(0, "a")), ("b", slow(0, "b"))], time.monotonic() + 5, 5, None, 1)
    assert key == "b"


def test_request_budget_limits_the_whole_chain(monkeypatch):
    monkeypatch.setattr(ai, "_candidates", lambda q, s, k: iter([("gemini:m", slow(30))]))
    monkeypatch.setattr(ai, "_gemini_provider", lambda: {"api_key": "test"})
    started = time.monotonic()
    with ai.request_budget(5):
        with pytest.raises(RuntimeError):
            ai.ask_fast("hello")
    assert time.monotonic() - started < 5.5
    assert ai.time_left() is None


def test_defaults_keep_answers_well_under_the_phone_limit():
    assert ai.FAST_BUDGET_SECONDS <= 40 and ai.FAST_MODEL_TIMEOUT_SECONDS <= 15 and ai.HEDGE_AFTER_SECONDS <= 8
    import app.main as m
    assert m.AI_REQUEST_BUDGET_SECONDS <= 50


def test_when_one_provider_is_slow_the_hedge_goes_to_another_provider():
    # Nov 21: every Gemini model timed out at once; walking them one by one used the whole budget.
    started = time.monotonic()
    chain = [("gemini:a", slow(30)), ("gemini:b", slow(30)), ("gemini:c", slow(30)), ("groq:x", slow(0.1, "groq answer"))]
    key, text = ai._run_chain(chain, started + 10, 8, 0.3, 2)
    assert key == "groq:x" and time.monotonic() - started < 1.5
