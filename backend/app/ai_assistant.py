import json
import logging
import os
import socket
import urllib.error
import urllib.request

OPENAI_URL = "https://api.openai.com/v1/responses"
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


def _request_profile(question: str) -> dict:
    if _is_complex_legal_request(question):
        return {
            "model": os.getenv("OPENAI_LEGAL_MODEL", os.getenv("OPENAI_MODEL", "gpt-5.6")).strip() or "gpt-5.6",
            "max_output_tokens": int(os.getenv("OPENAI_LEGAL_MAX_OUTPUT_TOKENS", "2200")),
            "reasoning": {"effort": os.getenv("OPENAI_LEGAL_REASONING_EFFORT", "medium")},
            "timeout": float(os.getenv("OPENAI_LEGAL_TIMEOUT_SECONDS", "55")),
        }
    return {
        "model": os.getenv("OPENAI_FAST_MODEL", os.getenv("OPENAI_MODEL", "gpt-5.6")).strip() or "gpt-5.6",
        "max_output_tokens": int(os.getenv("OPENAI_FAST_MAX_OUTPUT_TOKENS", "900")),
        "reasoning": {"effort": os.getenv("OPENAI_FAST_REASONING_EFFORT", "none")},
        "timeout": float(os.getenv("OPENAI_FAST_TIMEOUT_SECONDS", "30")),
    }


def ask_openai(question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.error("AI provider configuration failure: OPENAI_API_KEY is missing")
        raise RuntimeError("AI service is not configured")
    profile = _request_profile(question)
    model = profile["model"]
    payload = json.dumps({
        "model": model,
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": question,
        "max_output_tokens": profile["max_output_tokens"],
        "reasoning": profile["reasoning"],
    }).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_URL,
        data=payload,
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=profile["timeout"]) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        logger.error("AI provider HTTP failure: status=%s model=%s %s", exc.code, model, _provider_error_summary(detail))
        raise RuntimeError("AI provider request failed") from exc
    except urllib.error.URLError as exc:
        reason_type = type(getattr(exc, "reason", None)).__name__
        logger.error("AI provider network failure: model=%s reason_type=%s", model, reason_type)
        raise RuntimeError("AI provider is temporarily unreachable") from exc
    except (TimeoutError, socket.timeout) as exc:
        logger.error("AI provider timeout: model=%s", model)
        raise RuntimeError("AI provider timed out") from exc
    except ValueError as exc:
        logger.error("AI provider returned invalid JSON: model=%s", model)
        raise RuntimeError("AI provider returned an invalid response") from exc

    text = (data.get("output_text") or "").strip()
    if not text:
        parts = []
        for item in data.get("output", []):
            for part in item.get("content", []):
                if part.get("type") == "output_text" and part.get("text"):
                    parts.append(part["text"])
        text = "\n".join(parts).strip()
    if not text:
        logger.error("AI provider returned no output text: model=%s response_status=%s", model, data.get("status", "unknown"))
        raise RuntimeError("AI provider returned an empty response")
    return text
