import json
import logging
import os
import threading
import time
import socket
import urllib.error
import urllib.request

OPENAI_URL = "https://api.openai.com/v1/responses"
XAI_URL = "https://api.x.ai/v1/responses"
logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """You are GA.LAW.HELP, a Georgia-focused legal information and research assistant.
Give clear, calm, plain-language legal information, not legal representation.
Do not claim to be a lawyer and do not promise outcomes.
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


RATE_LIMIT_BACKOFF_SECONDS = float(os.getenv("AI_RATE_LIMIT_BACKOFF_SECONDS", "1.5"))
last_model_used = threading.local()


def _ask_gemini(provider: dict, question: str, speed: str | None = None, model_override: str | None = None) -> str:
    profile = _gemini_profile(question, provider["default_model"], speed)
    model = model_override or profile["model"]
    generation_config = {"maxOutputTokens": profile["max_output_tokens"]}
    if profile["thinking_level"]:
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
    if text and finish_reason == "MAX_TOKENS" and generation_config.get("responseMimeType") != "application/json":
        logger.warning("AI answer hit MAX_TOKENS: provider=gemini model=%s; trimmed to last full sentence", model)
        text = trim_to_last_sentence(text)
    if not text:
        finish = ((data.get("candidates") or [{}])[0] or {}).get("finishReason", "unknown")
        block = (data.get("promptFeedback") or {}).get("blockReason", "")
        logger.error("AI provider returned no output text: provider=gemini model=%s finish=%s block=%s", model, finish, block)
        raise RuntimeError("AI provider returned an empty response")
    return text


def _ask_provider(provider: dict, question: str, speed: str | None = None) -> str:
    if provider["name"] != "gemini":
        text = _ask_responses_api(provider, question)
        last_model_used.value = provider["name"] + ":" + _request_profile(question, provider["default_model"])["model"]
        logger.info("AI answered: provider=%s model=%s", provider["name"], last_model_used.value)
        return text
    primary = _gemini_profile(question, provider["default_model"], speed)["model"]
    lite = os.getenv("GEMINI_FAST_MODEL", GEMINI_FAST_DEFAULT_MODEL).strip() or GEMINI_FAST_DEFAULT_MODEL
    # On 429: retry the same model once after a short backoff, then the lite model (separate quota).
    attempts = [(primary, 0.0), (primary, RATE_LIMIT_BACKOFF_SECONDS)]
    if lite != primary:
        attempts.append((lite, 0.0))
    last = None
    for model, delay in attempts:
        if delay:
            time.sleep(delay)
        try:
            text = _ask_gemini(provider, question, speed, model_override=model)
            last_model_used.value = "gemini:" + model
            logger.info("AI answered: provider=gemini model=%s", model)
            return text
        except ProviderHTTPError as exc:
            last = exc
            if exc.status != 429:
                raise
            logger.warning("Gemini 429 on model=%s; trying next option", model)
    raise last


def ask_openai(question: str, speed: str | None = None) -> str:
    """Ask the active AI provider; falls back to the next configured provider on quota/auth errors."""
    providers = _providers()
    if not providers:
        logger.error("AI provider configuration failure: GEMINI_API_KEY, XAI_API_KEY and OPENAI_API_KEY are missing")
        raise RuntimeError("AI service is not configured")
    last_error = None
    for index, provider in enumerate(providers):
        try:
            return _ask_provider(provider, question, speed)
        except ProviderHTTPError as exc:
            last_error = exc
            if exc.status in FALLBACK_STATUS_CODES and index + 1 < len(providers):
                logger.warning("AI provider fallback: from=%s status=%s to=%s", provider["name"], exc.status, providers[index + 1]["name"])
                continue
            raise
    raise last_error  # pragma: no cover


def ask_fast(question: str) -> str:
    """Chat-style answers: always the fast profile (lite model, low thinking, capped output)."""
    return ask_openai(question, speed="fast")
