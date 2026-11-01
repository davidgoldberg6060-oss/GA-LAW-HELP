import json
from unittest import mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import ai_assistant, answer_cache
from app.grounded_legal_assistant import used_in_text, _authority_context


def test_trim_to_last_sentence():
    assert ai_assistant.trim_to_last_sentence("One. Two is done. Three such as petition") == "One. Two is done."
    assert ai_assistant.trim_to_last_sentence("Complete.") == "Complete."


def _resp(text, finish="STOP"):
    return {"candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": finish}]}


def test_max_tokens_answer_trimmed(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    with mock.patch.object(ai_assistant, "_http_post_json", return_value=_resp("A full sentence here. And then a cut", "MAX_TOKENS")):
        assert ai_assistant.ask_fast("what is a deposit") == "A full sentence here."


def test_429_rotates_chain_and_cools_down(monkeypatch):
    from app import ai_models
    ai_models.reset()
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODEL_CHAIN", "m-a,m-b,m-c")
    for v in ("XAI_API_KEY", "OPENAI_API_KEY", "AI_PROVIDER", "GROQ_API_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(v, raising=False)
    calls = []

    def fake(provider, model, url, payload, headers, timeout):
        calls.append(model)
        if model == "m-a":
            e = ai_assistant.ProviderHTTPError("quota", 429); e.detail = '"retryDelay": "30s"'; raise e
        if model == "m-b":
            e = ai_assistant.ProviderHTTPError("quota", 429); e.detail = "GenerateRequestsPerDayPerProjectPerModel-FreeTier"; raise e
        return _resp("Answer.")

    with mock.patch.object(ai_assistant, "_http_post_json", side_effect=fake):
        assert ai_assistant.ask_fast("x") == "Answer."
        assert ai_assistant.ask_fast("y") == "Answer."
    assert calls == ["m-a", "m-b", "m-c", "m-c"]  # cooling models skipped on the second request
    assert ai_assistant.last_model_used.value == "gemini:m-c"
    st = {r["model"]: r for r in ai_models.status()["chat_chain"]}
    assert st["gemini:m-a"]["cooling_down"] and st["gemini:m-a"]["seconds_left"] <= 30
    assert "daily" in st["gemini:m-b"]["reason"]
    ai_models.reset()


def test_compat_provider_used_only_when_key_set(monkeypatch):
    from app import ai_models
    ai_models.reset()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert all(p["name"] != "groq" for p in ai_models.compat_providers())
    monkeypatch.setenv("GROQ_API_KEY", "g")
    with mock.patch.object(ai_assistant, "_http_post_json", return_value={"choices": [{"message": {"content": "Hi."}, "finish_reason": "stop"}]}):
        assert ai_assistant.ask_fast("x") == "Hi."
    assert ai_assistant.last_model_used.value.startswith("groq:")


def test_daily_cooldown_until_pacific_midnight():
    from app import ai_models
    secs, reason = ai_models.cooldown_seconds("PerDay quota", None, now=1_793_500_000.0)
    assert 60 <= secs <= 24 * 3600 + 600 and "Pacific" in reason


def test_used_in_text_matches_sections_exactly():
    hit = {"citation": "O.C.G.A. § 44-7-34"}
    assert used_in_text(hit, "See O.C.G.A. § 44-7-34 (text as of 2022).")
    assert not used_in_text(hit, "See O.C.G.A. § 44-7-340.")
    assert not used_in_text({"citation": "O.C.G.A. § 40-9-39"}, "deposit returned under 44-7-34")


def test_context_is_capped_and_excerpted():
    hits = [{"citation": f"O.C.G.A. § 1-1-{i}", "excerpt": "word " * 500} for i in range(20)]
    ctx = _authority_context(hits)
    assert ctx.count("Citation:") == 8 and len(ctx) < 8 * 1500


def test_db_cache_shared_across_processes(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/c.db")
    db = sessionmaker(bind=engine)()
    answer_cache.clear(); answer_cache._table_ready = False
    answer_cache.put("Deposit?", "general", {"answer": "x"}, now=100.0, db=db)
    answer_cache.clear()  # simulate a different worker process
    assert answer_cache.get("deposit", "general", now=200.0, db=db) == {"answer": "x"}
    answer_cache.clear()
    assert answer_cache.get("deposit", "general", now=100.0 + answer_cache.TTL_SECONDS + 1, db=db) is None
    monkey_rows = answer_cache.DB_MAX_ROWS
    answer_cache.DB_MAX_ROWS = 3
    try:
        for i in range(6):
            answer_cache.put(f"q{i}", "general", {"answer": i}, now=300.0 + i, db=db)
        assert db.execute(answer_cache.text("SELECT COUNT(*) FROM public_answer_cache")).scalar() == 3
    finally:
        answer_cache.DB_MAX_ROWS = monkey_rows


def test_openrouter_free_only_with_headers_and_last(monkeypatch):
    from app import ai_models
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("OPENROUTER_API_KEY", "o")
    monkeypatch.setenv("OPENROUTER_MODELS", "paid/model,a/b:free")
    provs = ai_models.compat_providers()
    assert [p["name"] for p in provs][-1] == "openrouter"
    orp = provs[-1]
    assert orp["models"] == ["a/b:free"] and orp["headers"]["X-Title"] == "GA.LAW.HELP"
    seen = {}
    def fake(provider, model, url, payload, headers, timeout):
        seen.update(headers); seen["model"] = model
        return {"choices": [{"message": {"content": "Ok."}, "finish_reason": "stop"}]}
    with mock.patch.object(ai_assistant, "_http_post_json", side_effect=fake):
        assert ai_assistant._ask_compat(orp, "a/b:free", "x", "fast") == "Ok."
    assert seen["HTTP-Referer"].startswith("https://ga-law-help") and seen["model"] == "a/b:free"
