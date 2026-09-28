"""Conversation-oriented Georgia case analysis.

Keeps case facts and recent conversation together while delegating legal authority
retrieval to the existing grounded assistant. The service never manufactures a
citation or treats an unverified authority as support.
"""
from __future__ import annotations

from dataclasses import dataclass

from .grounded_legal_assistant import grounded_legal_response


@dataclass(frozen=True)
class CaseChatMessage:
    role: str
    content: str


def _recent_history(messages: list[CaseChatMessage], max_messages: int = 20) -> str:
    lines: list[str] = []
    for item in messages[-max_messages:]:
        role = (item.role or "").strip().lower()
        if role not in {"user", "assistant"}:
            continue
        content = (item.content or "").strip()
        if content:
            lines.append(f"{role.upper()}: {content[:6000]}")
    return "\n".join(lines)


def analyze_case_conversation(*, user_message: str, history: list[CaseChatMessage] | None,
                              case_summary: str | None, ask_ai) -> dict:
    question = (user_message or "").strip()
    if not question:
        raise ValueError("A case question or fact description is required.")

    parts: list[str] = []
    if case_summary and case_summary.strip():
        parts.append("CASE FILE CONTEXT (user/case supplied):\n" + case_summary.strip()[:12000])
    recent = _recent_history(history or [])
    if recent:
        parts.append("RECENT CASE CONVERSATION:\n" + recent)
    parts.append("CURRENT USER MESSAGE:\n" + question)
    retrieval_query = "\n\n".join(parts)

    def structured_ai(grounded_prompt: str) -> str:
        return ask_ai(grounded_prompt + """

CASE ANALYSIS INSTRUCTIONS:
Answer the user conversationally, then organize the useful analysis under these
headings when the facts and verified authority support them:
- What matters most
- Possible defenses or prosecution weaknesses
- Motions or remedies counsel may consider
- Evidence and constitutional issues
- What counsel may consider arguing or raising in court
- Questions to ask the lawyer / facts still needed
- Verified Georgia authorities
- Deadlines or procedural issues

Treat allegations as allegations. Identify missing facts. Never guarantee a motion,
defense, dismissal, sentence, or outcome. Never invent a statute, case, deadline, or
holding. If the authority corpus does not verify a proposition, label that proposition
as needing verification instead of presenting it as Georgia law. Do not tell a
represented user to disregard counsel.
""")

    result = grounded_legal_response(retrieval_query, "case_analysis", structured_ai)
    result["conversation"] = True
    result["user_message"] = question
    return result
