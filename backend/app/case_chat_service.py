"""Conversation-oriented case analysis built on verified Georgia authority retrieval."""
from __future__ import annotations

from dataclasses import dataclass

from .grounded_legal_assistant import grounded_legal_response


@dataclass(frozen=True)
class CaseChatMessage:
    role: str
    content: str


def _conversation_text(messages: list[CaseChatMessage], *, max_messages: int = 20) -> str:
    recent = messages[-max_messages:]
    lines: list[str] = []
    for message in recent:
        role = message.role.strip().lower()
        if role not in {"user", "assistant"}:
            continue
        content = message.content.strip()
        if content:
            lines.append(f"{role.upper()}: {content[:6000]}")
    return "\n".join(lines)


def analyze_case_conversation(
    *,
    user_message: str,
    history: list[CaseChatMessage] | None,
    case_summary: str | None,
    ask_ai,
) -> dict:
    """Answer one conversational case-analysis turn without fabricating authority."""
    question = (user_message or "").strip()
    if not question:
        raise ValueError("A case question or fact description is required.")

    history_text = _conversation_text(history or [])
    context_parts = []
    if case_summary and case_summary.strip():
        context_parts.append("CASE CONTEXT (user/case-file supplied):\n" + case_summary.strip()[:12000])
    if history_text:
        context_parts.append("RECENT CONVERSATION:\n" + history_text)
    context_parts.append("CURRENT USER MESSAGE:\n" + question)
    retrieval_query = "\n\n".join(context_parts)

    def structured_ai(grounded_prompt: str) -> str:
        instructions = """

CASE-CHAT RESPONSE FORMAT:
Respond conversationally first, then organize useful analysis under these headings when supported by the facts:
1. What matters most
2. Possible defenses or prosecution weaknesses
3. Motions/remedies counsel may consider
4. Evidence and constitutional issues
5. What counsel may consider arguing or raising in court
6. Questions to ask the lawyer / facts still needed
7. Verified Georgia authorities
8. Deadlines or procedural issues (only when supplied authority supports them)

Do not tell a represented person to ignore counsel. Do not present a suggested argument as guaranteed to work. Distinguish allegations, missing facts, general legal information, and authority-backed conclusions. If authority coverage is incomplete, say exactly which propositions still need verification rather than inventing support.
"""
        return ask_ai(grounded_prompt + instructions)

    result = grounded_legal_response(retrieval_query, "case_analysis", structured_ai)
    result["conversation"] = True
    result["user_message"] = question
    return result
