import json
import os
import socket
import urllib.error
import urllib.request

OPENAI_URL = "https://api.openai.com/v1/responses"

SYSTEM_INSTRUCTIONS = """You are GA.LAW.HELP, a Georgia-focused legal information and research assistant.
Give clear, calm, plain-language legal information, not legal representation.
Do not claim to be a lawyer and do not promise outcomes.
Distinguish known facts, assumptions, and issues that need verification.
For Georgia-law questions, reason carefully from the supplied verified authorities and facts. Never invent authority.
For each material legal conclusion, identify the factual premise, governing authority supplied in context, counterargument, and unresolved verification issue when applicable.
When dates matter, say that the law in effect on the relevant date must be checked.
For police encounters, prioritize physical safety: never encourage resistance, obstruction, evasion, destruction of evidence, or deception.
If a user describes an emergency or immediate danger, prioritize emergency help.
Keep answers structured and useful. End with a short reminder that the response is legal information, not legal advice."""

LEGAL_COMPLEXITY_MARKERS = (
    "MOTION SCREEN", "VERIFIED MOTION REGISTRY", "post-conviction", "appeal",
    "habeas", "suppress", "ineffective assistance", "constitutional", "sentencing",
    "jurisdiction", "indictment", "probation revocation", "new trial",
)


def _is_complex_legal_request(question: str) -> bool:
    lowered = question.lower()
    return len(question) >= 2500 or any(marker.lower() in lowered for marker in LEGAL_COMPLEXITY_MARKERS)


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
        raise RuntimeError("AI service is not configured")
    profile = _request_profile(question)
    payload = json.dumps({
        "model": profile["model"],
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": question,
        "max_output_tokens": profile["max_output_tokens"],
        "reasoning": profile["reasoning"],
    }).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_URL,
        data=payload,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=profile["timeout"]) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError("AI provider request failed: " + detail[:500]) from exc
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        raise RuntimeError("AI provider is temporarily unreachable or timed out") from exc
    text = (data.get("output_text") or "").strip()
    if not text:
        parts = []
        for item in data.get("output", []):
            for part in item.get("content", []):
                if part.get("type") == "output_text" and part.get("text"):
                    parts.append(part["text"])
        text = "\n".join(parts).strip()
    if not text:
        raise RuntimeError("AI provider returned an empty response")
    return text
