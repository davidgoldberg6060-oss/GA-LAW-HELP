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
        os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GROQ_API_KEY", "").strip())


def timeout_seconds() -> float:
    try:
        return max(0.5, float(os.getenv("CITATION_PROPOSAL_TIMEOUT_SECONDS", "2.5")))
    except ValueError:
        return 2.5


def _prompt(question: str) -> str:
    return (
        "You help a Georgia legal research tool find laws. Do not give advice.\n"
        "The user may write in slang or street language (e.g. 'fade'/'scrap'/'jumped' = fight/battery, "
        "'12'/'opps'/'feds' = police, 'locked up'/'booked' = arrested/jail, 'strap'/'blick'/'pole' = gun, "
        "'loud'/'gas'/'za' = marijuana, 'plug'/'trap'/'serving' = selling drugs, 'hit a lick' = robbery/theft, "
        "'boosting' = shoplifting, 'PO'/'violated' = probation violation, 'BM'/'baby mama' = child custody/support, "
        "'put out' = eviction).\n"
        f"QUESTION (user supplied, unverified):\n{question[-2500:]}\n\n"
        "1) Rewrite the question as 4-10 plain legal search words (e.g. 'self defense justification battery arrest').\n"
        f"2) List up to {MAX_SECTIONS} Official Code of Georgia Annotated section numbers most relevant to it "
        "(offense, defense, procedure, rights, or civil sections). Use only section numbers you are confident exist.\n"
        'Return ONLY JSON: {"search_terms":"...","sections":["16-3-21","17-6-1"]}'
    )


def parse_terms(raw: str) -> str:
    try:
        match = re.search(r"\{.*\}", raw or "", re.S)
        data = json.loads(match.group(0)) if match else {}
    except (ValueError, AttributeError):
        return ""
    terms = re.sub(r"[^A-Za-z0-9 \-]", " ", str(data.get("search_terms") or ""))
    return " ".join(terms.split()[:12])


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
    return propose(question, timeout)[0]


def propose(question: str, timeout: float | None = None) -> tuple[list[str], str]:
    """Quick model step: (likely O.C.G.A. sections, plain legal search terms). ([], "") on failure.
    Uses the fastest free model that is not cooling down (Gemini lite, then Groq)."""
    if not enabled() or not (question or "").strip():
        return [], ""
    from . import ai_assistant
    text = ai_assistant.ask_quick_json(_prompt(question), timeout if timeout is not None else timeout_seconds())
    return parse_sections(text), parse_terms(text)
