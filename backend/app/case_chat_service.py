"""Conversation context for grounded Georgia case analysis."""
from __future__ import annotations
from dataclasses import dataclass
from .grounded_legal_assistant import grounded_legal_response

@dataclass(frozen=True)
class CaseChatMessage:
    role: str
    content: str

def _recent_history(messages:list[CaseChatMessage],max_messages:int=20)->str:
    lines=[]
    for item in messages[-max_messages:]:
        role=(item.role or "").strip().lower()
        if role not in {"user","assistant"}:continue
        content=(item.content or "").strip()
        if content:lines.append(f"{role.upper()}: {content[:6000]}")
    return "\n".join(lines)

def analyze_case_conversation(*,user_message:str,history:list[CaseChatMessage]|None,case_summary:str|None,ask_ai)->dict:
    question=(user_message or "").strip()
    if not question:raise ValueError("A case question or fact description is required.")
    parts=[]
    if case_summary and case_summary.strip():parts.append("CASE FILE CONTEXT (user/case supplied):\n"+case_summary.strip()[:12000])
    recent=_recent_history(history or [])
    if recent:parts.append("RECENT CASE CONVERSATION:\n"+recent)
    parts.append("CURRENT USER MESSAGE:\n"+question)
    result=grounded_legal_response("\n\n".join(parts),"case_analysis",ask_ai)
    result["conversation"]=True
    result["user_message"]=question
    return result
