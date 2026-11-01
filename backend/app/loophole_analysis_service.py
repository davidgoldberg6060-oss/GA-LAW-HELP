"""Legal Loopholes: grounded analysis of contradictions, gaps, ambiguities and exceptions.

The user supplies a Georgia legal topic. We retrieve verified authorities (OCGA sections,
regulations, court opinions) with the same hybrid retrieval as the grounded assistant, ask the
model for structured findings, then validate every citation server-side: any finding citing an
authority that was not in the retrieved, verified set (or citing nothing) is dropped.

Findings are analysis of how the law is written and read, never instructions for evading it.
"""
from __future__ import annotations

import json
import re

from .grounded_legal_assistant import _authority_context, _hybrid_retrieval, _verified_hits

MAX_TOPIC_CHARS = 300
FINDING_TYPES = {"contradiction": "Contradiction", "gap": "Gap", "ambiguity": "Ambiguity", "exception": "Exception"}
DISCLAIMER = "This is legal information, not legal advice; talk to a Georgia attorney."
NONE_FOUND = "No contradictions, gaps, ambiguities or exceptions could be supported by the verified Georgia authorities retrieved for this topic."
REFUSAL = ("GA.LAW.HELP can't help with evading law enforcement, avoiding detection, or committing a crime. "
           "You can ask about how a Georgia law is written, its exceptions and defenses, or where courts have disagreed.")
COVERAGE_NOTE = "GA.LAW.HELP is still adding Georgia laws and court opinions to its library, so try again later or try a related topic."
SUGGESTED_TOPICS = ("Self-defense", "Landlord security deposits", "DUI", "Traffic stops", "Expungement / record restriction", "Eviction notice")

_UNSAFE = re.compile(
    r"(?i)\b(evade|evading|evasion|escape|outrun|flee|fleeing|hide|hiding|avoid(?:ing)?\s+(?:getting\s+)?(?:caught|arrest|detection|police|cops|the\s+law)|"
    r"get\s+away\s+with|without\s+(?:getting\s+)?caught|beat\s+(?:a|the)\s+(?:breathalyzer|drug\s+test)|destroy\s+evidence|"
    r"launder|fake\s+id|forge|tamper|intimidate\s+(?:a\s+)?witness|smuggl|traffick)\w*"
)


def is_unsafe_topic(topic: str) -> bool:
    return bool(_UNSAFE.search(topic or ""))


def _norm(c: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(c or "").lower())


def _prompt(topic: str, context: str) -> str:
    return f"""GA.LAW.HELP Legal Loopholes analysis.
TOPIC (user supplied): {topic}

TRACEABLE VERIFIED GEORGIA AUTHORITIES (the ONLY sources you may cite):
{context}

Task: Analyze the supplied authorities on this topic and identify:
(a) contradiction: tensions between provisions, or between statute and case law;
(b) gap: situations the text does not cover;
(c) ambiguity: wording courts have read differently or that is unclear;
(d) exception: exceptions and defenses written into the law.
Rules:
- Frame findings as neutral analysis of the law, never as instructions for evading the law, police, or detection.
- Each finding must cite one or more citations copied exactly from the 'Citation:' lines above. Never cite anything else.
- Do not invent text, holdings, deadlines or outcomes. If nothing is supported, return an empty list.
- If currency or precedential status is unknown, say so in the explanation.
Also write "lawyer_take": a plain-English "If I Was Your Lawyer, I Would Say" note of 3-6 sentences on what someone facing this topic should consider and practical lawful next steps (gather documents, deadlines the cited authorities mention, when to get a real Georgia attorney). Ground it only in the supplied authorities and cite them. Never suggest breaking the law, deceiving anyone, or evading police.
Write every text field in plain, friendly English with no markdown. Never mention the list of authorities, what sources were or were not supplied, the system, a database, or verification; talk to the user directly.
Return ONLY JSON: {{"findings":[{{"type":"contradiction|gap|ambiguity|exception","title":"short","explanation":"2-4 sentences","citations":["exact citation"]}}],"lawyer_take":{{"text":"3-6 sentences","citations":["exact citation"]}}}}"""


LAWYER_LABEL = "If I Was Your Lawyer, I Would Say"
LAWYER_DISCLAIMER = "Not legal advice \u2014 this app is not your lawyer."


def _parse_obj(raw) -> dict:
    m = re.search(r"\{.*\}", str(raw or ""), re.S)
    try:
        data = json.loads(m.group(0)) if m else {}
    except (ValueError, TypeError):
        data = {}
    return data if isinstance(data, dict) else {}


def validate_lawyer_take(raw, verified: list[dict]):
    """Return the lawyer take only if it has text and every citation was retrieved."""
    if not isinstance(raw, dict):
        return None
    text = str(raw.get("text") or "").strip()
    cites = raw.get("citations")
    if isinstance(cites, str):
        cites = [cites]
    if not text or not isinstance(cites, list) or not cites or is_unsafe_topic(text):
        return None
    kept, _ = validate_findings([{"type": "exception", "explanation": text, "citations": cites}], verified)
    if not kept:
        return None
    return {"label": LAWYER_LABEL, "text": text[:1500], "citations": kept[0]["citations"], "disclaimer": LAWYER_DISCLAIMER}


def _parse(raw) -> list:
    text = str(raw or "")
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except (ValueError, TypeError):
        return []
    items = data.get("findings") if isinstance(data, dict) else None
    return items if isinstance(items, list) else []


def validate_findings(items: list, verified: list[dict]) -> tuple[list[dict], int]:
    """Keep only findings whose every citation is in the retrieved verified set."""
    by_norm = {_norm(h.get("citation")): h for h in verified if _norm(h.get("citation"))}
    kept, dropped = [], 0
    for item in items:
        if not isinstance(item, dict):
            dropped += 1
            continue
        kind = str(item.get("type") or "").strip().lower()
        cites = item.get("citations")
        if isinstance(cites, str):
            cites = [cites]
        if kind not in FINDING_TYPES or not isinstance(cites, list) or not cites:
            dropped += 1
            continue
        matched = [by_norm.get(_norm(c)) for c in cites]
        explanation = str(item.get("explanation") or "").strip()
        if any(h is None for h in matched) or not explanation:
            dropped += 1
            continue
        kept.append({
            "type": kind,
            "type_label": FINDING_TYPES[kind],
            "title": str(item.get("title") or FINDING_TYPES[kind]).strip()[:200],
            "explanation": explanation[:2000],
            "citations": [{"citation": h.get("citation"), "title": h.get("title"), "source_url": h.get("source_url"),
                           "record_type": h.get("record_type"), "currency_status": h.get("currency_status") or "unknown",
                           "precedential_status": h.get("precedential_status") or "unknown"} for h in matched],
        })
    return kept, dropped


def analyze_loopholes(topic: str, ask_ai, db=None) -> dict:
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("Enter a Georgia legal topic to analyze.")
    if len(topic) > MAX_TOPIC_CHARS:
        raise ValueError(f"Topic is too long ({MAX_TOPIC_CHARS} characters or fewer).")
    base = {"topic": topic, "disclaimer": DISCLAIMER, "suggested_topics": list(SUGGESTED_TOPICS)}
    if is_unsafe_topic(topic):
        return {**base, "refused": True, "message": REFUSAL, "findings": [], "authorities": [], "dropped_findings": 0, "grounded_authority_count": 0, "lawyer_take": None}
    retrieval = _hybrid_retrieval(topic, "case_analysis", db, 15)
    verified = _verified_hits(retrieval)
    if not verified:
        return {**base, "refused": False, "message": "No verified Georgia authority was retrieved for this topic, so no findings can be shown. " + NONE_FOUND + " " + COVERAGE_NOTE,
                "findings": [], "authorities": [], "dropped_findings": 0, "grounded_authority_count": 0, "lawyer_take": None}
    raw = ask_ai(_prompt(topic, _authority_context(verified)))
    findings, dropped = validate_findings(_parse(raw), verified)
    lawyer_take = validate_lawyer_take(_parse_obj(raw).get("lawyer_take"), verified)
    return {**base, "refused": False, "message": None if findings else NONE_FOUND, "findings": findings,
            "authorities": [{"citation": h.get("citation"), "title": h.get("title"), "source_url": h.get("source_url")} for h in verified],
            "dropped_findings": dropped, "grounded_authority_count": len(verified), "lawyer_take": lawyer_take}
