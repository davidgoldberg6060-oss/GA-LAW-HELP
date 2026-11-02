import json
import logging
import os
import threading
import time
import socket
import urllib.error
import urllib.request

from . import ai_models

OPENAI_URL = "https://api.openai.com/v1/responses"
XAI_URL = "https://api.x.ai/v1/responses"
logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """You are GA.LAW.HELP, a Georgia-focused legal information and research assistant.
Give clear, calm, plain-language legal information, not legal representation.
Do not claim to be a lawyer and do not promise outcomes.
Do not assume the user is in jail or prison: most users are family or friends on the outside. Say "the person in custody" or "your loved one" and give steps an outside person can take, unless the user says it is them.
Distinguish known facts, assumptions, and issues that need verification.
For Georgia-law questions, reason carefully from supplied verified authorities and facts and never invent authority.
For each material legal conclusion, identify the factual premise, governing authority supplied in context, a meaningful counterargument when one exists, and unresolved verification issues.
Encourage verification against current official Georgia statutes, court rules, and controlling opinions.
When dates matter, say that the law in effect on the relevant date must be checked.
For police encounters, prioritize physical safety: never encourage resistance, obstruction, evasion, destruction of evidence, or deception.
If a user describes an emergency or immediate danger, prioritize emergency help.
Keep answers structured and useful. End with a short reminder that the response is legal information, not legal advice."""

LEGAL_COMPLEXITY_MARKERS = (
    "motion screen", "verified motion registry", "post-conviction", "appeal", "habeas",
    "suppress", "ineffective assistance", "constitutional", "sentencing", "jurisdiction",
    "indictment", "probation revocation", "new trial",
)


def _provider_error_summary(raw: str) -> str:
    """Return provider error metadata without logging prompts, keys, or response bodies."""
    try:
        parsed = json.loads(raw)
        error = parsed.get("error", {}) if isinstance(parsed, dict) else {}
        if isinstance(error, dict):
            error_type = str(error.get("type") or "unknown")[:80]
            error_code = str(error.get("code") or "unknown")[:80]
            param = str(error.get("param") or "")[:80]
            return f"type={error_type} code={error_code}" + (f" param={param}" if param else "")
    except (TypeError, ValueError):
        pass
    return "unparseable_provider_error"


def _is_complex_legal_request(question: str) -> bool:
    lowered = question.lower()
    return len(question) >= 2500 or any(marker in lowered for marker in LEGAL_COMPLEXITY_MARKERS)


GEMINI_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_DEFAULT_MODEL = "gemini-3.5-flash"
# Chat-style answers (Talk to Me, Know Your Rights, case chat) use the lite model: ~1 s instead of ~20 s.
GEMINI_FAST_DEFAULT_MODEL = "gemini-3.5-flash-lite"
FALLBACK_STATUS_CODES = {401, 402, 403, 429}


class ProviderHTTPError(RuntimeError):
    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.status = status


def _openai_provider() -> dict:
    return {
        "name": "openai",
        "url": os.getenv("OPENAI_API_URL", OPENAI_URL).strip() or OPENAI_URL,
        "api_key": os.getenv("OPENAI_API_KEY", "").strip(),
        "default_model": os.getenv("OPENAI_MODEL", "gpt-5.6").strip() or "gpt-5.6",
    }


def _xai_provider() -> dict:
    return {
        "name": "xai",
        "url": os.getenv("XAI_API_URL", XAI_URL).strip() or XAI_URL,
        "api_key": os.getenv("XAI_API_KEY", "").strip(),
        "default_model": os.getenv("XAI_MODEL", "grok-4").strip() or "grok-4",
    }


def _gemini_provider() -> dict:
    return {
        "name": "gemini",
        "url": os.getenv("GEMINI_API_URL", GEMINI_URL_BASE).strip().rstrip("/") or GEMINI_URL_BASE,
        "api_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "default_model": os.getenv("GEMINI_MODEL", GEMINI_DEFAULT_MODEL).strip() or GEMINI_DEFAULT_MODEL,
    }


_PROVIDER_BUILDERS = {"gemini": _gemini_provider, "xai": _xai_provider, "openai": _openai_provider}
_DEFAULT_ORDER = ("gemini", "xai", "openai")


def _providers() -> list:
    """Configured providers in priority order: AI_PROVIDER first, then gemini, xai, openai."""
    preferred = os.getenv("AI_PROVIDER", "").strip().lower()
    order = list(_DEFAULT_ORDER)
    if preferred in _PROVIDER_BUILDERS:
        order.remove(preferred)
        order.insert(0, preferred)
    configured = [p for p in (_PROVIDER_BUILDERS[name]() for name in order) if p["api_key"]]
    return configured


def _provider() -> dict:
    providers = _providers()
    return providers[0] if providers else _openai_provider()


def _request_profile(question: str, default_model: str) -> dict:
    if _is_complex_legal_request(question):
        return {
            "model": os.getenv("OPENAI_LEGAL_MODEL", default_model).strip() or default_model,
            "max_output_tokens": int(os.getenv("OPENAI_LEGAL_MAX_OUTPUT_TOKENS", "2200")),
            "reasoning": {"effort": os.getenv("OPENAI_LEGAL_REASONING_EFFORT", "medium")},
            "timeout": float(os.getenv("OPENAI_LEGAL_TIMEOUT_SECONDS", "55")),
        }
    return {
        "model": os.getenv("OPENAI_FAST_MODEL", default_model).strip() or default_model,
        "max_output_tokens": int(os.getenv("OPENAI_FAST_MAX_OUTPUT_TOKENS", "900")),
        "reasoning": {"effort": os.getenv("OPENAI_FAST_REASONING_EFFORT", "none")},
        "timeout": float(os.getenv("OPENAI_FAST_TIMEOUT_SECONDS", "30")),
    }


def _http_post_json(provider: dict, model: str, url: str, payload: dict, headers: dict, timeout: float) -> dict:
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        logger.error("AI provider HTTP failure: provider=%s status=%s model=%s %s", provider["name"], exc.code, model, _provider_error_summary(detail))
        err = ProviderHTTPError("AI provider request failed", exc.code)
        err.detail = detail[:2000]
        err.retry_after = (exc.headers.get("Retry-After") if exc.headers else None)
        raise err from exc
    except urllib.error.URLError as exc:
        reason_type = type(getattr(exc, "reason", None)).__name__
        logger.error("AI provider network failure: provider=%s model=%s reason_type=%s", provider["name"], model, reason_type)
        raise RuntimeError("AI provider is temporarily unreachable") from exc
    except (TimeoutError, socket.timeout) as exc:
        logger.error("AI provider timeout: provider=%s model=%s", provider["name"], model)
        raise RuntimeError("AI provider timed out") from exc
    except ValueError as exc:
        logger.error("AI provider returned invalid JSON: provider=%s model=%s", provider["name"], model)
        raise RuntimeError("AI provider returned an invalid response") from exc


def _ask_responses_api(provider: dict, question: str) -> str:
    profile = _request_profile(question, provider["default_model"])
    model = profile["model"]
    data = _http_post_json(
        provider, model, provider["url"],
        {
            "model": model,
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": question,
            "max_output_tokens": profile["max_output_tokens"],
            "reasoning": profile["reasoning"],
        },
        {"Authorization": "Bearer " + provider["api_key"], "Content-Type": "application/json"},
        profile["timeout"],
    )
    text = (data.get("output_text") or "").strip()
    if not text:
        parts = []
        for item in data.get("output", []):
            for part in item.get("content", []):
                if part.get("type") == "output_text" and part.get("text"):
                    parts.append(part["text"])
        text = "\n".join(parts).strip()
    if not text:
        logger.error("AI provider returned no output text: provider=%s model=%s response_status=%s", provider["name"], model, data.get("status", "unknown"))
        raise RuntimeError("AI provider returned an empty response")
    return text


def _gemini_profile(question: str, default_model: str, speed: str | None = None) -> dict:
    if speed != "fast" and (speed == "quality" or _is_complex_legal_request(question)):
        return {
            "model": os.getenv("GEMINI_LEGAL_MODEL", default_model).strip() or default_model,
            "max_output_tokens": int(os.getenv("GEMINI_LEGAL_MAX_OUTPUT_TOKENS", "4096")),
            "thinking_level": os.getenv("GEMINI_LEGAL_THINKING_LEVEL", "medium").strip(),
            "timeout": float(os.getenv("GEMINI_LEGAL_TIMEOUT_SECONDS", "55")),
        }
    return {
        "model": os.getenv("GEMINI_FAST_MODEL", GEMINI_FAST_DEFAULT_MODEL).strip() or GEMINI_FAST_DEFAULT_MODEL,
        "max_output_tokens": int(os.getenv("GEMINI_FAST_MAX_OUTPUT_TOKENS", "2400")),
        "thinking_level": os.getenv("GEMINI_FAST_THINKING_LEVEL", "low").strip(),
        "timeout": float(os.getenv("GEMINI_FAST_TIMEOUT_SECONDS", "20")),
    }


def trim_to_last_sentence(text: str) -> str:
    """End a truncated answer cleanly at its last complete sentence (or line)."""
    text = (text or "").rstrip()
    if not text or text[-1] in ".!?)\"”:":
        return text
    cut = max(text.rfind(". "), text.rfind(".\n"), text.rfind("! "), text.rfind("? "), text.rfind("?\n"), text.rfind("!\n"))
    if cut >= len(text) * 0.4:
        return text[: cut + 1].rstrip()
    nl = text.rfind("\n")
    return text[:nl].rstrip() if nl >= len(text) * 0.4 else text + "…"


last_model_used = threading.local()


def _ask_gemini(provider: dict, question: str, speed: str | None = None, model_override: str | None = None, timeout_cap: float | None = None) -> str:
    profile = _gemini_profile(question, provider["default_model"], speed)
    if timeout_cap:
        profile["timeout"] = max(5.0, min(profile["timeout"], timeout_cap))
    model = model_override or profile["model"]
    generation_config = {"maxOutputTokens": profile["max_output_tokens"]}
    if profile["thinking_level"] and not model.startswith("gemini-2."):  # 2.x models use thinkingBudget, not thinkingLevel
        generation_config["thinkingConfig"] = {"thinkingLevel": profile["thinking_level"]}
    stripped = question.lstrip()
    if stripped.startswith("{") or "return only json" in question.lower() or "respond with json" in question.lower():
        generation_config["responseMimeType"] = "application/json"
    def _call(config):
        return _http_post_json(
            provider, model, f"{provider['url']}/{model}:generateContent",
            {
                "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTIONS}]},
                "contents": [{"role": "user", "parts": [{"text": question}]}],
                "generationConfig": config,
            },
            {"x-goog-api-key": provider["api_key"], "Content-Type": "application/json"},
            profile["timeout"],
        )
    try:
        data = _call(generation_config)
    except ProviderHTTPError as exc:
        # A model that rejects the thinking setting (HTTP 400) is retried once without it.
        if exc.status != 400 or "thinkingConfig" not in generation_config or "thinking" not in str(getattr(exc, "detail", "")).lower():
            raise
        generation_config = {k: v for k, v in generation_config.items() if k != "thinkingConfig"}
        data = _call(generation_config)
    parts = []
    for candidate in (data.get("candidates") or [])[:1]:
        for part in (candidate.get("content") or {}).get("parts") or []:
            if part.get("text") and not part.get("thought"):
                parts.append(part["text"])
    text = "".join(parts).strip()
    finish_reason = ((data.get("candidates") or [{}])[0] or {}).get("finishReason", "")
    if finish_reason == "MAX_TOKENS" and generation_config.get("responseMimeType") == "application/json":
        logger.warning("AI JSON answer hit MAX_TOKENS: provider=gemini model=%s (may be incomplete)", model)
    if text and finish_reason == "MAX_TOKENS" and generation_config.get("responseMimeType") != "application/json":
        logger.warning("AI answer hit MAX_TOKENS: provider=gemini model=%s; trimmed to last full sentence", model)
        text = trim_to_last_sentence(text)
    if not text:
        finish = ((data.get("candidates") or [{}])[0] or {}).get("finishReason", "unknown")
        block = (data.get("promptFeedback") or {}).get("blockReason", "")
        logger.error("AI provider returned no output text: provider=gemini model=%s finish=%s block=%s", model, finish, block)
        raise RuntimeError("AI provider returned an empty response")
    return text


def _ask_compat(provider: dict, model: str, question: str, speed: str | None) -> str:
    """OpenAI-compatible chat-completions call (Groq, OpenRouter, Cerebras, Mistral, GitHub Models...)."""
    fast = speed == "fast" or (speed != "quality" and not _is_complex_legal_request(question))
    data = _http_post_json(
        provider, model, provider["url"],
        {"model": model, "max_tokens": 2400 if fast else 4096,
         "messages": [{"role": "system", "content": SYSTEM_INSTRUCTIONS}, {"role": "user", "content": question}]},
        {"Authorization": "Bearer " + provider["api_key"], "Content-Type": "application/json",
         "User-Agent": "GA.LAW.HELP/1.6 (+https://ga-law-help-production.up.railway.app)", **(provider.get("headers") or {})},
        20.0 if fast else 55.0,
    )
    choice = (data.get("choices") or [{}])[0] or {}
    text = ((choice.get("message") or {}).get("content") or "").strip()
    if text and choice.get("finish_reason") == "length" and not question.lstrip().startswith("{"):
        text = trim_to_last_sentence(text)
    if not text:
        raise RuntimeError("AI provider returned an empty response")
    return text


def _chain_kind(question: str, speed: str | None) -> str:
    return "check" if speed != "fast" and (speed == "quality" or _is_complex_legal_request(question)) else "chat"


def _answered(key: str, started: float, text: str) -> str:
    last_model_used.value = key
    logger.info("AI answered: model=%s seconds=%.1f", key, time.monotonic() - started)
    return text


def _try_model(key: str, call):
    """Run one model call; returns text or None (after putting the model on cooldown when appropriate)."""
    if ai_models.is_cooling(key):
        return None
    try:
        return call()
    except ProviderHTTPError as exc:
        detail = str(getattr(exc, "detail", ""))
        if exc.status == 429 or (exc.status != 400 and "RESOURCE_EXHAUSTED" in detail):
            seconds, reason = ai_models.cooldown_seconds(detail, getattr(exc, "retry_after", None))
            ai_models.mark_cooldown(key, seconds, reason)
        elif exc.status in (404,) or (exc.status == 400 and "not found" in detail.lower()):
            ai_models.mark_cooldown(key, ai_models.UNAVAILABLE_COOLDOWN_SECONDS, "model unavailable")
        elif exc.status == 400:
            # A bad request is about the prompt, not the model: stop instead of burning every model's quota.
            raise RuntimeError("AI provider rejected the request") from exc
        elif exc.status in (401, 403):
            ai_models.mark_cooldown(key, ai_models.UNAVAILABLE_COOLDOWN_SECONDS, f"auth error {exc.status}")
        elif exc.status >= 500:
            ai_models.mark_cooldown(key, 30.0, f"server error {exc.status}")
        else:
            logger.warning("AI model failed: model=%s status=%s", key, exc.status)
        return None
    except RuntimeError as exc:
        logger.warning("AI model failed: model=%s error=%s", key, exc)
        if "timed out" in str(exc):
            ai_models.mark_cooldown(key, 90.0, "timeout")
        return None


def ask_openai(question: str, speed: str | None = None) -> str:
    """Free-model rotation: Gemini chain (fastest-first for chat, quality-first for checks), then any
    OpenAI-compatible free providers with keys set, then xAI/OpenAI. Cooling-down models are skipped."""
    started = time.monotonic()
    budget = float(os.getenv("AI_CHAIN_BUDGET_SECONDS", "50"))
    gemini = _gemini_provider()
    kind = _chain_kind(question, speed)
    if gemini["api_key"]:
        # Leave time for the free fallback providers: Gemini may use ~60% of the budget, and one slow
        # model can't eat it all (a timeout also puts that model on a short cooldown).
        gemini_budget = budget * 0.6
        for model in ai_models.gemini_chain(kind):
            left = gemini_budget - (time.monotonic() - started)
            if left < 5:
                break
            text = _try_model("gemini:" + model, lambda m=model, cap=min(left, 25.0): _ask_gemini(gemini, question, speed, model_override=m, timeout_cap=cap))
            if text:
                return _answered("gemini:" + model, started, text)
    for provider in ai_models.compat_providers():
        for model in provider["models"]:
            if time.monotonic() - started > budget:
                break
            text = _try_model(provider["name"] + ":" + model, lambda p=provider, m=model: _ask_compat(p, m, question, speed))
            if text:
                return _answered(provider["name"] + ":" + model, started, text)
    others = [p for p in _providers() if p["name"] != "gemini"]
    for provider in others:
        model = _request_profile(question, provider["default_model"])["model"]
        text = _try_model(provider["name"] + ":" + model, lambda p=provider: _ask_responses_api(p, question))
        if text:
            return _answered(provider["name"] + ":" + model, started, text)
    if not gemini["api_key"] and not others and not ai_models.compat_providers():
        logger.error("AI provider configuration failure: no AI provider keys are set")
        raise RuntimeError("AI service is not configured")
    logger.error("AI unavailable: every model in the %s chain failed or is cooling down", kind)
    raise RuntimeError("AI provider is temporarily unavailable")


def refresh_listed_models() -> None:
    """For providers with a public model list (OpenRouter), cool down configured ids that have disappeared."""
    for provider in ai_models.compat_providers():
        if not provider.get("list_url"):
            continue
        try:
            req = urllib.request.Request(provider["list_url"], headers={"User-Agent": "GA.LAW.HELP"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                listed = {m.get("id") for m in json.loads(resp.read().decode("utf-8")).get("data", [])}
        except Exception as exc:  # list check is best-effort
            logger.warning("Model list check failed: provider=%s error=%s", provider["name"], type(exc).__name__)
            continue
        for model in provider["models"]:
            key = provider["name"] + ":" + model
            if model in listed:
                ai_models.record_probe(key, True, "listed")
            else:
                ai_models.record_probe(key, False, "not listed")
                ai_models.mark_cooldown(key, ai_models.UNAVAILABLE_COOLDOWN_SECONDS, "model no longer listed")


def probe_models() -> None:
    """1-token liveness check of every configured Gemini model (run once in the background at startup)."""
    refresh_listed_models()
    gemini = _gemini_provider()
    if not gemini["api_key"]:
        return
    for model in dict.fromkeys(ai_models.gemini_chain("chat") + ai_models.gemini_chain("check")):
        key = "gemini:" + model
        try:
            _http_post_json(gemini, model, f"{gemini['url']}/{model}:generateContent",
                            {"contents": [{"role": "user", "parts": [{"text": "hi"}]}], "generationConfig": {"maxOutputTokens": 1}},
                            {"x-goog-api-key": gemini["api_key"], "Content-Type": "application/json"}, 15.0)
            ai_models.record_probe(key, True, "ok")
        except ProviderHTTPError as exc:
            ai_models.record_probe(key, exc.status == 429, f"http {exc.status}")
            _try_model(key, lambda e=exc: (_ for _ in ()).throw(e))
        except RuntimeError as exc:
            ai_models.record_probe(key, False, str(exc))


def ask_fast(question: str) -> str:
    """Chat-style answers: always the fast profile (lite model, low thinking, capped output)."""
    return ask_openai(question, speed="fast")


def background_model_checks() -> None:
    """Startup probe, then re-check listed (OpenRouter :free) models every 6 hours."""
    probe_models()
    while True:
        time.sleep(float(os.getenv("AI_MODEL_LIST_REFRESH_SECONDS", "21600")))
        refresh_listed_models()


def ask_quick_json(prompt: str, timeout: float = 2.5) -> str:
    """Tiny JSON helper for query rewrite / citation hints: fastest non-cooling free model, short budget."""
    started = time.monotonic()
    gemini = _gemini_provider()
    tries = []
    if gemini["api_key"]:
        for model in [m for m in ai_models.gemini_chain("chat") if "lite" in m][:2]:
            tries.append(("gemini:" + model, lambda m=model: _http_post_json(
                gemini, m, f"{gemini['url']}/{m}:generateContent",
                {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                 "generationConfig": {"maxOutputTokens": 300, "responseMimeType": "application/json", "temperature": 0}},
                {"x-goog-api-key": gemini["api_key"], "Content-Type": "application/json"}, max(0.5, timeout - (time.monotonic() - started)))))
    for provider in ai_models.compat_providers():
        if provider["name"] == "openrouter":
            continue  # 50 requests/day: keep for real answers
        for model in provider["models"][:2]:
            tries.append((provider["name"] + ":" + model, lambda p=provider, m=model: _http_post_json(
                p, m, p["url"],
                {"model": m, "max_tokens": 400, "temperature": 0, "messages": [{"role": "user", "content": prompt}]},
                {"Authorization": "Bearer " + p["api_key"], "Content-Type": "application/json",
                 "User-Agent": "GA.LAW.HELP/1.6", **(p.get("headers") or {})}, max(0.5, timeout - (time.monotonic() - started)))))
    for key, call in tries:
        if time.monotonic() - started > timeout:
            break
        try:
            data = _try_model(key, call)
        except RuntimeError:
            data = None
        if not data:
            continue
        if "candidates" in data:
            return "".join(part.get("text", "") for cand in (data.get("candidates") or [])[:1]
                           for part in (cand.get("content") or {}).get("parts") or [] if not part.get("thought"))
        return (((data.get("choices") or [{}])[0] or {}).get("message") or {}).get("content") or ""
    return ""
