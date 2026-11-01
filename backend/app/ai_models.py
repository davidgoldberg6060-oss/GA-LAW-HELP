"""Free-model rotation: Gemini model chains with per-model cooldowns, plus env-driven
OpenAI-compatible free providers (Groq, OpenRouter :free, Cerebras, Mistral, GitHub Models).

No prompt contents are ever logged here."""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import re
import threading
import time
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# All "Free of charge" on the Gemini API Free Tier per ai.google.dev/gemini-api/docs/pricing (checked 2026-11-01).
DEFAULT_CHAT_CHAIN = ("gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-2.5-flash-lite,gemini-3.5-flash,"
                      "gemini-3.6-flash,gemini-3-flash-preview,gemini-2.5-flash,gemini-3.8-flash")
DEFAULT_CHECK_CHAIN = ("gemini-3.8-flash,gemini-3.5-flash,gemini-3.6-flash,gemini-2.5-pro,gemini-3-flash-preview,"
                       "gemini-2.5-flash,gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-2.5-flash-lite")
SHORT_COOLDOWN_SECONDS = float(os.getenv("AI_MODEL_COOLDOWN_SECONDS", "60"))
UNAVAILABLE_COOLDOWN_SECONDS = 6 * 3600
PACIFIC = ZoneInfo("America/Los_Angeles")

# OpenAI-compatible providers appended after Gemini when their key env var is set (skipped otherwise).
# Extra ones can be added with OPENAI_COMPAT_PROVIDERS='[{"name":..,"url":..,"key_env":..,"models":[..]}]'.
COMPAT_PROVIDERS = (
    {"name": "groq", "key_env": "GROQ_API_KEY", "url": "https://api.groq.com/openai/v1/chat/completions",
     "models_env": "GROQ_MODELS", "models": "openai/gpt-oss-120b,openai/gpt-oss-20b,qwen/qwen3-32b"},
    {"name": "openrouter", "key_env": "OPENROUTER_API_KEY", "url": "https://openrouter.ai/api/v1/chat/completions",
     "models_env": "OPENROUTER_MODELS", "models": "meta-llama/llama-3.3-70b-instruct:free"},
    {"name": "cerebras", "key_env": "CEREBRAS_API_KEY", "url": "https://api.cerebras.ai/v1/chat/completions",
     "models_env": "CEREBRAS_MODELS", "models": "llama-3.3-70b"},
    {"name": "mistral", "key_env": "MISTRAL_API_KEY", "url": "https://api.mistral.ai/v1/chat/completions",
     "models_env": "MISTRAL_MODELS", "models": "mistral-small-latest"},
    {"name": "github", "key_env": "GITHUB_MODELS_TOKEN", "url": "https://models.github.ai/inference/chat/completions",
     "models_env": "GITHUB_MODELS", "models": "openai/gpt-4.1-mini"},
)

_lock = threading.Lock()
_cooldowns: dict[str, dict] = {}  # "provider:model" -> {"until": epoch, "reason": str}
_probe: dict[str, dict] = {}


def _split(value: str) -> list[str]:
    return [m.strip() for m in (value or "").split(",") if m.strip()]


def gemini_chain(kind: str) -> list[str]:
    if kind == "check":
        chain = _split(os.getenv("GEMINI_CHECK_MODEL_CHAIN", "") or DEFAULT_CHECK_CHAIN)
        pinned = [os.getenv("GEMINI_LEGAL_MODEL", "").strip(), os.getenv("GEMINI_MODEL", "").strip()]
        explicit = os.getenv("GEMINI_CHECK_MODEL_CHAIN", "")
    else:
        chain = _split(os.getenv("GEMINI_MODEL_CHAIN", "") or DEFAULT_CHAT_CHAIN)
        pinned = [os.getenv("GEMINI_FAST_MODEL", "").strip()]
        explicit = os.getenv("GEMINI_MODEL_CHAIN", "")
    if not explicit:  # legacy single-model settings go to the front of the default chain
        chain = [m for m in pinned if m] + chain
    return list(dict.fromkeys(chain))


def compat_providers() -> list[dict]:
    specs = list(COMPAT_PROVIDERS)
    try:
        specs += json.loads(os.getenv("OPENAI_COMPAT_PROVIDERS", "") or "[]")
    except ValueError:
        logger.warning("OPENAI_COMPAT_PROVIDERS is not valid JSON; ignored")
    out = []
    for spec in specs:
        key = os.getenv(spec.get("key_env", ""), "").strip()
        if not key or not spec.get("url"):
            continue
        models = spec.get("models")
        models = _split(os.getenv(spec.get("models_env", ""), "")) or (models if isinstance(models, list) else _split(models or ""))
        out.append({"name": spec["name"], "url": spec["url"], "api_key": key, "models": models})
    return out


def next_pacific_midnight(now: float | None = None) -> float:
    current = _dt.datetime.fromtimestamp(now if now is not None else time.time(), PACIFIC)
    tomorrow = (current + _dt.timedelta(days=1)).date()
    return _dt.datetime.combine(tomorrow, _dt.time(0, 5), PACIFIC).timestamp()


def cooldown_seconds(detail: str, retry_after: str | None, now: float | None = None) -> tuple[float, str]:
    """How long to rest a model after a 429/quota error, and why."""
    text = detail or ""
    if re.search(r"(?i)per ?day|PerDay|daily", text):
        now = time.time() if now is None else now
        return max(60.0, next_pacific_midnight(now) - now), "daily quota (until midnight Pacific)"
    if retry_after:
        try:
            return max(1.0, float(retry_after)), "rate limit (retry-after)"
        except ValueError:
            pass
    m = re.search(r'"retryDelay"\s*:\s*"(\d+(?:\.\d+)?)s"', text)
    if m:
        return max(1.0, float(m.group(1))), "rate limit (retryDelay)"
    return SHORT_COOLDOWN_SECONDS, "rate limit"


def mark_cooldown(key: str, seconds: float, reason: str, now: float | None = None) -> None:
    now = time.time() if now is None else now
    with _lock:
        _cooldowns[key] = {"until": now + seconds, "reason": reason}
    logger.warning("AI model cooling down: model=%s seconds=%d reason=%s", key, int(seconds), reason)


def is_cooling(key: str, now: float | None = None) -> bool:
    now = time.time() if now is None else now
    with _lock:
        item = _cooldowns.get(key)
        if item and item["until"] > now:
            return True
        _cooldowns.pop(key, None)
        return False


def reset() -> None:
    with _lock:
        _cooldowns.clear(); _probe.clear()


def record_probe(key: str, ok: bool, status: str) -> None:
    with _lock:
        _probe[key] = {"ok": ok, "status": status, "checked_at": int(time.time())}


def status(now: float | None = None) -> dict:
    now = time.time() if now is None else now
    def view(key):
        with _lock:
            cd = _cooldowns.get(key); pr = _probe.get(key)
        row = {"model": key, "cooling_down": bool(cd and cd["until"] > now)}
        if row["cooling_down"]:
            row["seconds_left"] = int(cd["until"] - now); row["reason"] = cd["reason"]
        if pr:
            row["probe"] = pr
        return row
    return {
        "chat_chain": [view("gemini:" + m) for m in gemini_chain("chat")],
        "check_chain": [view("gemini:" + m) for m in gemini_chain("check")],
        "extra_providers": [view(p["name"] + ":" + m) for p in compat_providers() for m in p["models"]],
    }
