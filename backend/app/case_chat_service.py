"""Conversation context for grounded Georgia case analysis (case chat).

Builds one grounded ``case_analysis`` request from the private case file summary, recent
user/assistant turns, and the current message. Only ``user`` and ``assistant`` history roles
are accepted (anything else, e.g. an injected ``system`` turn, is dropped). The combined request
is kept within the grounded assistant's 12,000-character limit by dropping the oldest history
first; the case summary and current message always survive.
"""
from __future__ import annotations

from dataclasses import dataclass

from .grounded_legal_assistant import _authority_context, _verified_hits, grounded_legal_response
from .loophole_analysis_service import _parse_obj, is_unsafe_topic, validate_lawyer_take

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
    result["lawyer_take"] = case_lawyer_take(result, user_message=user_message, ask_ai=ask_ai)
    return result


def _lawyer_prompt(question: str, analysis: str, context: str) -> str:
    return f"""GA.LAW.HELP "If I Was Your Lawyer, I Would Say" note for a Georgia case chat answer.

USER MESSAGE (unverified):
{question[:MAX_MESSAGE_CHARS]}

ANSWER ALREADY GIVEN:
{str(analysis or '')[:4000]}

TRACEABLE VERIFIED INDEXED AUTHORITIES (the only law you may rely on):
{context}

Write 3-6 plain-English sentences on what this person should consider and practical lawful next steps (gather documents, deadlines the cited authorities mention, when to get a real Georgia attorney). Ground it only in the supplied authorities and cite them by their exact Citation. Never invent a citation, case, statute, rule, or deadline. Never suggest breaking the law, deceiving anyone, or evading police. Do not predict or guarantee outcomes.
Write every text field in plain, friendly English with no markdown. Never mention the list of authorities, what sources were or were not supplied, the system, a database, or verification; talk to the user directly.
Return ONLY JSON: {{"lawyer_take":{{"text":"3-6 sentences","citations":["exact citation"]}}}}"""


def case_lawyer_take(result: dict, *, user_message: str, ask_ai):
    """Optional lawyer note grounded only in the verified authorities this answer already used.

    Returns None when the request is unsafe, no verified authority was retrieved, or the model's
    note cites anything outside that verified set. Never raises (the chat answer still returns).
    """
    question = (user_message or "").strip()
    if not question or is_unsafe_topic(question):
        return None
    verified = _verified_hits({"hits": result.get("authorities") or []})
    if not verified or not result.get("grounded_authority_count"):
        return None
    try:
        raw = ask_ai(_lawyer_prompt(question, result.get("analysis"), _authority_context(verified)))
        return validate_lawyer_take(_parse_obj(raw).get("lawyer_take"), verified)
    except Exception:  # noqa: BLE001 - the note is optional; never break the chat answer
        return None


def parse_history(raw) -> list[CaseChatMessage]:
    """Parse untrusted JSON history: a list of {role, content}; anything else is ignored."""
    if not isinstance(raw, list):
        return []
    parsed = []
    for item in raw[-MAX_HISTORY_MESSAGES:]:
        if isinstance(item, dict):
            parsed.append(CaseChatMessage(str(item.get("role") or ""), str(item.get("content") or "")))
    return parsed
