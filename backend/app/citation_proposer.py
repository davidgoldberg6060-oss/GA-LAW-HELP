"""Quick model step for AI grounding: propose likely O.C.G.A. sections for a question.

The proposals are only retrieval hints. Every proposed section is looked up by exact citation
in the persisted corpus and dropped when it is not there, so nothing the model says becomes
legal support unless the verified record exists.
"""
from __future__ import annotations

import json
import logging
import os
import re

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-3.5-flash-lite"
_SECTION = re.compile(r"^(?:O\.?C\.?G\.?A\.?\s*§*\s*)?(\d{1,2}[A-Z]?-\d{1,3}[A-Z]?-\d{1,4}(?:\.\d+)?)$")
MAX_SECTIONS = 8


def enabled() -> bool:
    return os.getenv("CITATION_PROPOSALS", "on").strip().lower() not in {"0", "off", "false", "no"} and bool(
        os.getenv("GEMINI_API_KEY", "").strip())


def timeout_seconds() -> float:
    try:
        return max(0.5, float(os.getenv("CITATION_PROPOSAL_TIMEOUT_SECONDS", "2.5")))
    except ValueError:
        return 2.5


def _prompt(question: str) -> str:
    return (
        "You help a Georgia legal research tool find statutes. Do not give advice.\n"
        f"QUESTION (user supplied, unverified):\n{question[-2500:]}\n\n"
        f"List up to {MAX_SECTIONS} Official Code of Georgia Annotated section numbers most relevant to this "
        "question (offense, procedure, rights, or civil sections). Use only section numbers you are confident exist.\n"
        'Return ONLY JSON: {"sections":["44-7-50","17-5-1"]}'
    )


def parse_sections(raw: str) -> list[str]:
    try:
        match = re.search(r"\{.*\}", raw or "", re.S)
        data = json.loads(match.group(0)) if match else {}
    except (ValueError, AttributeError):
        return []
    out: list[str] = []
    for value in data.get("sections") or []:
        m = _SECTION.match(str(value).strip())
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out[:MAX_SECTIONS]


def propose_sections(question: str, timeout: float | None = None) -> list[str]:
    """Ask a small fast Gemini model for likely sections. Returns [] on any failure."""
    if not enabled() or not (question or "").strip():
        return []
    from . import ai_assistant
    provider = ai_assistant._gemini_provider()
    model = os.getenv("GEMINI_CITATION_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    try:
        data = ai_assistant._http_post_json(
            provider, model, f"{provider['url']}/{model}:generateContent",
            {
                "contents": [{"role": "user", "parts": [{"text": _prompt(question)}]}],
                "generationConfig": {"maxOutputTokens": 200, "responseMimeType": "application/json", "temperature": 0},
            },
            {"x-goog-api-key": provider["api_key"], "Content-Type": "application/json"},
            timeout if timeout is not None else timeout_seconds(),
        )
    except Exception as exc:  # network, quota, timeout: grounding continues without proposals
        logger.warning("Citation proposal skipped: %s", type(exc).__name__)
        return []
    text = "".join(
        part.get("text", "")
        for cand in (data.get("candidates") or [])[:1]
        for part in (cand.get("content") or {}).get("parts") or []
        if not part.get("thought")
    )
    return parse_sections(text)
