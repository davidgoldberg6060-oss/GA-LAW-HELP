"""Conversation context for grounded Georgia case analysis (case chat).

Builds one grounded ``case_analysis`` request from the private case file summary, recent
user/assistant turns, and the current message. Only ``user`` and ``assistant`` history roles
are accepted (anything else, e.g. an injected ``system`` turn, is dropped). The combined request
is kept within the grounded assistant's 12,000-character limit by dropping the oldest history
first; the case summary and current message always survive.
"""
from __future__ import annotations

from dataclasses import dataclass

from .grounded_legal_assistant import grounded_legal_response

MAX_REQUEST_CHARS = 12_000
MAX_MESSAGE_CHARS = 4_000
MAX_SUMMARY_CHARS = 4_000
MAX_HISTORY_MESSAGES = 20
MAX_TURN_CHARS = 2_000
_ROLES = {"user", "assistant"}


@dataclass(frozen=True)
class CaseChatMessage:
    role: str
    content: str


def case_summary_from_case(case) -> str:
    """Case-file context in the same shape the motion screen uses (user supplied, unverified)."""
    fields = (
        ("Case title", case.title),
        ("Case number", getattr(case, "case_number", None)),
        ("Georgia county", getattr(case, "county", None)),
        ("Case type", getattr(case, "case_type", None)),
        ("Current stage", getattr(case, "stage", None)),
        ("Case narrative", getattr(case, "narrative", None)),
    )
    return "\n".join(f"{label}: {(value or 'Not entered')}" for label, value in fields)


def _history_lines(messages: list[CaseChatMessage]) -> list[str]:
    lines = []
    for item in messages[-MAX_HISTORY_MESSAGES:]:
        role = (item.role or "").strip().lower()
        if role not in _ROLES:
            continue
        content = (item.content or "").strip()
        if content:
            lines.append(f"{role.upper()}: {content[:MAX_TURN_CHARS]}")
    return lines


def build_case_chat_request(*, user_message: str, history: list[CaseChatMessage] | None, case_summary: str | None) -> str:
    question = (user_message or "").strip()
    if not question:
        raise ValueError("A case question or fact description is required.")
    if len(question) > MAX_MESSAGE_CHARS:
        raise ValueError("Message is too long. Use the key facts and question (4,000 characters or fewer).")
    head = []
    if case_summary and case_summary.strip():
        summary = case_summary.strip()
        if len(summary) > MAX_SUMMARY_CHARS:
            summary = summary[:MAX_SUMMARY_CHARS] + "\n[Case text truncated for analysis]"
        head.append("CASE FILE CONTEXT (user/case supplied, not independently verified):\n" + summary)
    tail = "CURRENT USER MESSAGE:\n" + question
    lines = _history_lines(history or [])
    header = "RECENT CASE CONVERSATION:\n"

    def assemble(kept: list[str]) -> str:
        parts = list(head)
        if kept:
            parts.append(header + "\n".join(kept))
        parts.append(tail)
        return "\n\n".join(parts)

    while lines and len(assemble(lines)) > MAX_REQUEST_CHARS:
        lines = lines[1:]  # drop the oldest turn first
    return assemble(lines)


def analyze_case_conversation(*, user_message: str, history: list[CaseChatMessage] | None, case_summary: str | None, ask_ai, db=None) -> dict:
    request = build_case_chat_request(user_message=user_message, history=history, case_summary=case_summary)
    result = grounded_legal_response(request, "case_analysis", ask_ai, db=db)
    result["conversation"] = True
    result["user_message"] = (user_message or "").strip()
    return result


def parse_history(raw) -> list[CaseChatMessage]:
    """Parse untrusted JSON history: a list of {role, content}; anything else is ignored."""
    if not isinstance(raw, list):
        return []
    parsed = []
    for item in raw[-MAX_HISTORY_MESSAGES:]:
        if isinstance(item, dict):
            parsed.append(CaseChatMessage(str(item.get("role") or ""), str(item.get("content") or "")))
    return parsed
