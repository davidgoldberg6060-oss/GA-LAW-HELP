"""Charge Check: "What could I be charged with?" for a user-described Georgia situation.

Two-step grounded flow (no slow full-text/case-law search):
1. The model proposes candidate O.C.G.A. section numbers for the situation (and we always add a
   fixed list of sentencing-alternative/procedure sections). Each candidate is looked up by EXACT
   citation in ``legal_authorities``; anything not found, not verified, or negatively treated is
   dropped. The model never supplies legal text.
2. The model writes likely charges, possible defenses/weak spots, and lawful ways toward the lowest
   outcome, citing only the verified sections from step 1. A validator drops any item citing an
   unretrieved authority, any item with evasion/obstruction advice, and any penalty statement that
   is not a verbatim quote from the retrieved section text.

Everything is an estimate: actual charges depend on police and the prosecutor.
"""
from __future__ import annotations

import json
import re

from .grounded_legal_assistant import _authority_context, _verified_hits
from .loophole_analysis_service import _norm, _parse_obj, validate_lawyer_take

MAX_SITUATION_CHARS = 4000
MAX_CANDIDATES = 14
LEVELS = {"misdemeanor": "Misdemeanor", "high_and_aggravated_misdemeanor": "High and aggravated misdemeanor",
          "felony": "Felony", "unknown": "Level not stated in retrieved text"}
DEFENSE_KINDS = {"missing_element": "Element the State must prove", "statutory_defense": "Defense or exception in the law",
                 "procedural": "Procedure / suppression issue"}
# Always looked up: lawful paths to a lower outcome and common procedural protections.
OUTCOME_SECTIONS = ("42-8-60", "42-8-62", "16-13-2", "35-3-37", "17-7-170", "17-7-171", "17-3-1", "15-18-80", "42-8-34")

ESTIMATE_NOTE = ("These are estimates based on the facts you typed. The actual charges depend on what police "
                 "report and what the prosecutor decides to file.")
DISCLAIMER = ("This is legal information, not legal advice. Talk to a Georgia criminal defense lawyer or "
              "public defender before you decide anything.")
RIGHTS_REMINDER = ("You have the right to remain silent. Don't talk to police or anyone else about the case "
                   "without a lawyer. If you can't afford a lawyer, ask the court for a public defender.")
REFUSAL = ("GA.LAW.HELP can't help with lying, hiding or destroying evidence, fleeing, contacting witnesses or "
           "victims, or hiding assets. Describe what happened and you'll get likely charges, lawful defenses, "
           "and lawful ways to get the lowest outcome.")
NONE_FOUND = ("No likely charge could be matched to a verified Georgia Code section in GA.LAW.HELP's library for "
              "this situation. Talk to a Georgia criminal defense lawyer or public defender.")
EMERGENCY = {
    "message": "If anyone is in danger right now, call 911.",
    "resources": [
        {"label": "Emergency", "contact": "911"},
        {"label": "988 Suicide & Crisis Lifeline", "contact": "Call or text 988"},
        {"label": "Georgia Crisis & Access Line", "contact": "1-800-715-4225"},
        {"label": "National Domestic Violence Hotline", "contact": "1-800-799-7233"},
    ],
}

# Evasion / obstruction advice that must never appear in the output (and requests for it are refused).
_EVASION = re.compile(
    r"(?i)\b(lie|lying|lied)\s+(to|about)\b|\bmake\s+up\s+(a|an)\s+(story|alibi)|\bfalse\s+(alibi|statement|story)|"
    r"\b(destroy|delete|wipe|hide|get\s+rid\s+of|burn|dispose\s+of|throw\s+away)\w*\s+(\w+\s+){0,3}(evidence|phone|gun|weapon|drugs|messages|texts|footage|video|videos|recording|camera|body|clothes|records)\b|"
    r"\b(leave\s+the\s+(state|country)|skip\s+(court|bail|bond)|miss\s+(your\s+)?court\s+date|don'?t\s+show\s+up\s+(to|for)\s+court)\b|"
    r"\b(contact|call|text|message|threaten|pressure|pay|bribe|convince|talk\s+to)\w*\s+(the\s+)?(witness|witnesses|victim|victims|accuser)\b|"
    r"\bhide\s+(my|your|the)?\s*(money|assets|property)|\b(transfer|move)\s+(my|your)?\s*assets\b|"
    r"\bcoach\s+(a|the)\s+witness|\bget\s+(the\s+)?(victim|witness)\s+to\s+(drop|recant|change)"
)
_EMERGENCY = re.compile(
    r"(?i)\b(bleeding|unconscious|not\s+breathing|overdos\w*|kill\s+(myself|me|him|her|them)|suicid\w*|"
    r"hurt\s+(myself|me)|he'?s\s+going\s+to\s+(hurt|kill)|she'?s\s+going\s+to\s+(hurt|kill)|right\s+now.{0,30}(hit|beat|attack|threat)\w*|"
    r"(hitting|beating|choking|strangling|attacking)\s+(me|her|him)|has\s+a\s+gun|kidnap\w*|trapped|in\s+danger)\b"
)
_SECTION = re.compile(r"^\s*(?:o\.?c\.?g\.?a\.?\s*)?(?:§+\s*)?(\d{1,2}[A-Za-z]?-\d{1,3}[A-Za-z]?-\d{1,4}(?:\.\d{1,3})?)\s*$", re.I)


_EVASION_REQUEST = re.compile(
    r"(?i)\b(how\s+(do|can|should|could)\s+i|should\s+i|can\s+i|help\s+me|i\s+(want|need|plan)\s+to|best\s+way\s+to|ways?\s+to)\s+"
    r"(\w+\s+){0,3}(lie|destroy|delete|wipe|hide|get\s+rid\s+of|dispose|flee|run\s+from|skip\s+(court|bail|bond)|leave\s+the\s+(state|country)|"
    r"get\s+away\s+with|not\s+get\s+caught|avoid\s+(getting\s+)?caught|evade|threaten|bribe|pay\s+off|make\s+the\s+(victim|witness)|"
    r"get\s+the\s+(victim|witness)|contact\s+the\s+(victim|witness)|move\s+my\s+(money|assets))"
)


def is_evasion_request(text: str) -> bool:
    """Situations may describe past conduct (e.g. 'I ran'); refuse only requests for help evading."""
    return bool(_EVASION_REQUEST.search(text or ""))


def is_evasion(text: str) -> bool:
    """Output filter: advice to lie, destroy/hide evidence, skip court, contact witnesses, hide assets."""
    return bool(_EVASION.search(text or "")) or bool(_EVASION_REQUEST.search(text or ""))


def is_emergency(text: str) -> bool:
    return bool(_EMERGENCY.search(text or ""))


def normalize_section(value) -> str | None:
    """'O.C.G.A. § 16-8-2' / '16-8-2' -> '16-8-2'; anything else -> None."""
    m = _SECTION.match(str(value or ""))
    return m.group(1) if m else None


def ocga_citation(section: str) -> str:
    return f"O.C.G.A. § {section}"


def lookup_sections(db, sections: list[str]) -> list[dict]:
    """Exact-citation lookup (uses the citation index). Returns grounded-hit dicts."""
    if db is None or not sections:
        return []
    from .models import LegalAuthority
    cites = [ocga_citation(s) for s in dict.fromkeys(sections)]
    rows = db.query(LegalAuthority).filter(LegalAuthority.citation.in_(cites)).all()
    order = {c: i for i, c in enumerate(cites)}
    rows = sorted(rows, key=lambda r: order.get(r.citation, 999))
    seen, hits = set(), []
    for row in rows:
        if row.citation in seen:
            continue
        seen.add(row.citation)
        hits.append({
            "title": row.title or row.citation, "citation": row.citation, "source_url": row.source_url,
            "verification_status": (row.status or "").lower(), "excerpt": (row.text or "")[:1800],
            "full_text": row.text or "", "record_type": row.authority_type,
            "currency_status": row.currency_status or "unknown", "precedential_status": row.precedential_status or "unknown",
            "negative_treatment": [row.negative_treatment] if row.negative_treatment else [],
            "authority_id": row.id,
        })
    return hits


def _candidate_prompt(situation: str, case_summary: str | None) -> str:
    extra = f"\nCASE FILE (user supplied):\n{case_summary[:3000]}\n" if case_summary else ""
    return f"""You help a Georgia criminal-law research tool find statutes. Do not give advice here.
SITUATION (user supplied, unverified):
{situation}
{extra}
List up to 10 Official Code of Georgia Annotated section numbers that police or a prosecutor would most likely look at for this situation: the offense sections (mostly Title 16, Title 40 for traffic/DUI e.g. 40-6-391, etc.), their grading/penalty sections if separate, and statutory defenses that could apply (e.g. 16-3-21 self-defense). Use only section numbers you are confident exist.
Return ONLY JSON: {{"sections":["16-8-2","16-8-12"]}}"""


def _analysis_prompt(situation: str, case_summary: str | None, context: str) -> str:
    extra = f"\nCASE FILE (user supplied, unverified):\n{case_summary[:3000]}\n" if case_summary else ""
    return f"""GA.LAW.HELP Charge Check (Georgia). A person describes a situation; estimate what they could be charged with and lawful ways to defend it and reach the lowest lawful outcome.
SITUATION (user supplied, unverified):
{situation}
{extra}
VERIFIED GEORGIA AUTHORITIES (the ONLY sources you may cite; copy citations exactly from the 'Citation:' lines):
{context}

Rules:
- Cite only the citations above. Never invent a citation, case, statute text, penalty, deadline or outcome.
- "penalty_quote" must be copied word-for-word from a 'Stored excerpt' above (the sentence stating punishment); if no punishment text is shown, use "".
- "level" is misdemeanor, high_and_aggravated_misdemeanor, felony, or unknown, and only from the cited text.
- Defenses: elements the State must prove that the facts may not show (missing_element), defenses/exceptions written in the law (statutory_defense), or procedural/suppression issues such as an unlawful search, Miranda/voluntariness, speedy trial, statute of limitations (procedural).
- Lowest outcome: lawful options only (lawyer/public defender, pretrial diversion, First Offender, conditional discharge, accountability courts, negotiating a plea to a lesser charge, probation/community service instead of jail, restitution, record restriction) and only where a cited section supports it.
- NEVER suggest lying, making up a story, destroying or hiding evidence, fleeing, skipping court, contacting/pressuring witnesses or victims, or hiding assets.
- Also write lawyer_take: 3-6 sentences, "If I Was Your Lawyer, I Would Say", lawful steps only, citing the authorities.
Return ONLY JSON:
{{"charges":[{{"charge":"name","citation":"exact","level":"misdemeanor|high_and_aggravated_misdemeanor|felony|unknown","penalty_quote":"verbatim or empty","why":"1-2 sentences tying facts to the law"}}],
"defenses":[{{"kind":"missing_element|statutory_defense|procedural","title":"short","explanation":"2-3 sentences","citations":["exact"]}}],
"lowest_outcome":[{{"title":"short","explanation":"2-3 sentences","citations":["exact"]}}],
"lawyer_take":{{"text":"3-6 sentences","citations":["exact"]}}}}"""


_LEVEL_WORDS = {"misdemeanor": ("misdemeanor",), "high_and_aggravated_misdemeanor": ("high and aggravated",),
                "felony": ("felony", "imprisonment for not less than one", "years")}


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _cite_view(h: dict) -> dict:
    return {"citation": h.get("citation"), "title": h.get("title"), "source_url": h.get("source_url"),
            "record_type": h.get("record_type"), "currency_status": h.get("currency_status") or "unknown"}


def _match(cites, by_norm):
    if isinstance(cites, str):
        cites = [cites]
    if not isinstance(cites, list) or not cites:
        return None
    matched = [by_norm.get(_norm(c)) or by_norm.get(_norm(ocga_citation(normalize_section(c) or "?"))) for c in cites]
    return None if any(m is None for m in matched) else matched


def validate_charge_check(data: dict, verified: list[dict]) -> tuple[dict, int]:
    """Keep only items fully grounded in ``verified`` and free of evasion advice."""
    by_norm = {_norm(h.get("citation")): h for h in verified if _norm(h.get("citation"))}
    dropped = 0
    charges, defenses, outcomes = [], [], []
    for item in data.get("charges") or []:
        if not isinstance(item, dict):
            dropped += 1; continue
        name = str(item.get("charge") or "").strip()
        matched = _match(item.get("citation"), by_norm)
        why = str(item.get("why") or "").strip()
        if not name or not matched:  # names/facts may lawfully mention e.g. "fleeing or attempting to elude"
            dropped += 1; continue
        hit = matched[0]
        quote = str(item.get("penalty_quote") or "").strip()
        verified_quote = quote if quote and len(quote) >= 12 and _ws(quote) in _ws(hit.get("full_text") or hit.get("excerpt")) else ""
        level = str(item.get("level") or "unknown").strip().lower()
        body = _ws(hit.get("full_text") or hit.get("excerpt"))
        if level not in LEVELS or (level != "unknown" and not any(w in body for w in _LEVEL_WORDS[level])):
            level = "unknown"
        charges.append({"charge": name[:200], "citation": _cite_view(hit), "level": level, "level_label": LEVELS[level],
                        "penalty": verified_quote[:800] or None,
                        "penalty_note": None if verified_quote else "Penalty not quoted; read the cited section or ask a lawyer.",
                        "why": why[:600]})
    for key, out, kinds in (("defenses", defenses, DEFENSE_KINDS), ("lowest_outcome", outcomes, None)):
        for item in data.get(key) or []:
            if not isinstance(item, dict):
                dropped += 1; continue
            kind = str(item.get("kind") or "").strip().lower()
            expl = str(item.get("explanation") or "").strip()
            title = str(item.get("title") or "").strip()
            matched = _match(item.get("citations"), by_norm)
            if (kinds and kind not in kinds) or not expl or not matched or is_evasion(title + " " + expl):
                dropped += 1; continue
            row = {"title": (title or "Option")[:200], "explanation": expl[:1500], "citations": [_cite_view(h) for h in matched]}
            if kinds:
                row.update(kind=kind, kind_label=kinds[kind])
            out.append(row)
    return {"charges": charges, "defenses": defenses, "lowest_outcome": outcomes}, dropped


def _base(situation: str, emergency: bool) -> dict:
    return {"situation": situation, "estimate_note": ESTIMATE_NOTE, "disclaimer": DISCLAIMER,
            "rights_reminder": RIGHTS_REMINDER, "emergency": EMERGENCY if emergency else None,
            "refused": False, "message": None, "charges": [], "defenses": [], "lowest_outcome": [],
            "authorities": [], "lawyer_take": None, "dropped_items": 0, "grounded_authority_count": 0}


def analyze_charge_check(situation: str, ask_ai, db=None, *, case_summary: str | None = None, lookup=None) -> dict:
    situation = (situation or "").strip()
    if not situation:
        raise ValueError("Describe what happened to check possible charges.")
    if len(situation) > MAX_SITUATION_CHARS:
        raise ValueError(f"Description is too long ({MAX_SITUATION_CHARS} characters or fewer).")
    result = _base(situation, is_emergency(situation))
    if is_evasion_request(situation):
        return {**result, "refused": True, "message": REFUSAL}
    lookup = lookup or (lambda sections: lookup_sections(db, sections))
    raw = _parse_obj(ask_ai(_candidate_prompt(situation, case_summary)))
    proposed = raw.get("sections") if isinstance(raw.get("sections"), list) else []
    sections = [s for s in (normalize_section(x) for x in proposed[:MAX_CANDIDATES]) if s]
    verified = _verified_hits({"hits": lookup(sections + list(OUTCOME_SECTIONS))})
    offense = [h for h in verified if normalize_section(h.get("citation")) in sections]
    if not offense:
        return {**result, "message": NONE_FOUND,
                "authorities": [_cite_view(h) for h in verified], "grounded_authority_count": len(verified)}
    data = _parse_obj(ask_ai(_analysis_prompt(situation, case_summary, _authority_context(verified))))
    kept, dropped = validate_charge_check(data, verified)
    take = validate_lawyer_take(data.get("lawyer_take"), verified)
    if take and is_evasion(take["text"]):
        take = None
    return {**result, **kept, "message": None if kept["charges"] else NONE_FOUND, "lawyer_take": take,
            "authorities": [_cite_view(h) for h in verified], "dropped_items": dropped,
            "grounded_authority_count": len(verified)}


def charge_check_note_text(result: dict) -> str:
    """Plain-text copy of a Charge Check saved to the case notes."""
    lines = ["CHARGE CHECK (estimate)", result.get("estimate_note") or "", "", "Situation: " + (result.get("situation") or "")]
    if result.get("charges"):
        lines.append("\nLIKELY CHARGES")
        for c in result["charges"]:
            lines.append(f"- {c['charge']} ({c['citation']['citation']}) - {c['level_label']}")
            if c.get("penalty"):
                lines.append(f"  Penalty text: \"{c['penalty']}\"")
    for key, label in (("defenses", "POSSIBLE DEFENSES AND WEAK SPOTS"), ("lowest_outcome", "WAYS TO GET THE LOWEST OUTCOME")):
        if result.get(key):
            lines.append("\n" + label)
            for d in result[key]:
                lines.append(f"- {d['title']}: {d['explanation']} [{', '.join(c['citation'] for c in d['citations'])}]")
    if result.get("lawyer_take"):
        lines += ["\nIF I WAS YOUR LAWYER, I WOULD SAY", result["lawyer_take"]["text"]]
    if result.get("message"):
        lines += ["", result["message"]]
    lines += ["", result.get("rights_reminder") or "", result.get("disclaimer") or ""]
    return "\n".join(lines)[:20000]
