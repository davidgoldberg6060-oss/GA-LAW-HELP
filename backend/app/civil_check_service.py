"""Civil Case Check: a user describes a Georgia civil dispute; we identify likely claims and
defenses, the court, deadlines, evidence to gather, weak spots for each side, and low-cost paths.

Same grounding contract as Charge Check: the model proposes O.C.G.A. sections, each is looked up
by EXACT citation in the database, unverified ones are dropped, and a validator removes any item
citing an unretrieved authority, any dollar limit/deadline that is not a verbatim quote from the
retrieved text, and any advice to lie, hide assets or destroy evidence.
"""
from __future__ import annotations

import re

from .charge_check_service import (EMERGENCY, _cite_view, _match, _ws, is_emergency, is_evasion,
                                   is_evasion_request, lookup_sections, normalize_section,
                                   with_amendment_note)
from .civil_topics import topic_sections
from .grounded_legal_assistant import _authority_context, _verified_hits, used_in_text
import json as _json
import os as _os
# Checks quote penalties/limits from the text, so they get longer excerpts than chat.
CHECK_EXCERPT_CHARS = int(_os.getenv("AI_CHECK_EXCERPT_CHARS", "2500"))
from .loophole_analysis_service import _parse_obj, validate_lawyer_take

MAX_SITUATION_CHARS = 4000
MAX_CANDIDATES = 14
COURTS = {"magistrate": "Magistrate Court (small claims)", "state": "State Court", "superior": "Superior Court",
          "probate": "Probate Court", "juvenile": "Juvenile Court", "unknown": "Court not confirmed by the retrieved text"}
SIDES = {"you": "Your side", "other_side": "Other side"}
# Always looked up: court jurisdiction and common limitation periods.
BASE_SECTIONS = ("15-10-2", "15-6-8", "15-7-4", "15-9-30", "15-11-10", "9-3-24", "9-3-25", "9-3-33", "9-3-31")

ESTIMATE_NOTE = ("This is an estimate based on the facts you typed. The other side's story, the documents and "
                 "the judge decide how a civil case actually comes out.")
DISCLAIMER = ("This is legal information, not legal advice. Talk to a Georgia lawyer or a legal aid office "
              "before you decide anything or miss a deadline.")
REFUSAL = ("GA.LAW.HELP can't help with lying, hiding or moving assets to avoid a judgment, destroying or "
           "faking evidence, or pressuring witnesses. Describe the dispute and you'll get the likely claims, "
           "lawful defenses, deadlines and low-cost ways to resolve it.")
NONE_FOUND = ("No claim or defense could be matched to a verified Georgia Code section in GA.LAW.HELP's library "
              "for this dispute. Georgia Legal Aid or the court's self-help center can point you to the right law.")
HELP_RESOURCES = [
    {"title": "Georgia Legal Aid (free civil legal help outside metro Atlanta)", "url": "https://www.glsp.org/"},
    {"title": "Atlanta Legal Aid Society (metro Atlanta)", "url": "https://atlantalegalaid.org/"},
    {"title": "Georgia Courts self-help (forms and court help)", "url": "https://georgiacourts.gov/a2j/"},
    {"title": "State Bar of Georgia — find a lawyer / referral", "url": "https://www.gabar.org/public/find-a-lawyer"},
]


def _candidate_prompt(situation: str, case_summary: str | None) -> str:
    extra = f"\nCASE FILE (user supplied):\n{case_summary[:3000]}\n" if case_summary else ""
    return f"""You help a Georgia civil-law research tool find statutes. Do not give advice here.
DISPUTE (user supplied, unverified):
{situation}
{extra}
List up to 10 Official Code of Georgia Annotated section numbers most relevant to this civil dispute: the claim or right (e.g. Title 44 landlord-tenant, Title 19 domestic relations, Title 13 contracts, Title 51 torts, Title 10 consumer, Title 34 labor, Title 53 probate), defenses, the statute of limitations (Title 9 Chapter 3), and court jurisdiction (e.g. 15-10-2 magistrate court). Use only section numbers you are confident exist.
Return ONLY JSON: {{"sections":["44-7-34","44-7-35"]}}"""


def _analysis_prompt(situation: str, case_summary: str | None, context: str) -> str:
    extra = f"\nCASE FILE (user supplied, unverified):\n{case_summary[:3000]}\n" if case_summary else ""
    return f"""GA.LAW.HELP Civil Case Check (Georgia). A person describes a civil dispute. Identify the likely claims or defenses, the court, deadlines, evidence to gather, weak spots for each side, and the lowest-cost lawful ways to resolve it.
DISPUTE (user supplied, unverified):
{situation}
{extra}
VERIFIED GEORGIA AUTHORITIES (the ONLY sources you may cite; copy citations exactly from the 'Citation:' lines):
{context}

Rules:
- Cite only the citations above. Never invent a citation, case, statute text, dollar amount, deadline or outcome.
- "court" is magistrate, state, superior, probate, juvenile or unknown. "limit_quote" must be copied word-for-word from a 'Stored excerpt' (e.g. the magistrate court dollar limit); otherwise "".
- Each deadline "quote" must be copied word-for-word from a 'Stored excerpt'; skip a deadline you cannot quote.
- "side" is "you" (claims/defenses the user can raise) or "other_side" (what the other party may argue).
- Weak spots: honest problems for each side (missing proof, missed deadline, exceptions in the law).
- Low-cost paths: lawful options only (demand letter, negotiation/settlement, mediation, small claims in magistrate court, legal aid, court self-help), citing a section where one supports it.
- NEVER suggest lying, faking or destroying evidence, hiding or moving assets, ignoring court papers, or pressuring witnesses.
- Also write lawyer_take: 3-6 sentences, "If I Was Your Lawyer, I Would Say", lawful steps only, citing the authorities.
Return ONLY JSON:
{{"claims":[{{"side":"you|other_side","claim":"name","citation":"exact","why":"1-2 sentences tying facts to the law"}}],
"court":{{"court":"magistrate|state|superior|probate|juvenile|unknown","why":"1-2 sentences","citation":"exact or empty","limit_quote":"verbatim or empty"}},
"deadlines":[{{"title":"short","quote":"verbatim","citation":"exact"}}],
"evidence":["item to gather"],
"weak_spots":[{{"side":"you|other_side","title":"short","explanation":"2-3 sentences","citations":["exact"]}}],
"low_cost_paths":[{{"title":"short","explanation":"2-3 sentences","citations":["exact or none"]}}],
"lawyer_take":{{"text":"3-6 sentences","citations":["exact"]}}}}"""


def _in_text(quote: str, hit: dict) -> bool:
    q = _ws(quote)
    return len(q) >= 12 and q in _ws(hit.get("full_text") or hit.get("excerpt"))


def validate_civil_check(data: dict, verified: list[dict]) -> tuple[dict, int]:
    """Keep only items grounded in ``verified`` and free of evasion advice."""
    from .loophole_analysis_service import _norm
    by_norm = {_norm(h.get("citation")): h for h in verified if _norm(h.get("citation"))}
    dropped = 0
    claims, deadlines, weak, paths, evidence = [], [], [], [], []
    for item in data.get("claims") or []:
        if not isinstance(item, dict):
            dropped += 1; continue
        name = str(item.get("claim") or "").strip(); why = str(item.get("why") or "").strip()
        side = str(item.get("side") or "you").strip().lower()
        matched = _match(item.get("citation"), by_norm)
        if not name or not matched or side not in SIDES or is_evasion(name + " " + why):
            dropped += 1; continue
        claims.append({"claim": name[:200], "side": side, "side_label": SIDES[side], "citation": _cite_view(matched[0]), "why": why[:600]})
    court = None
    raw_court = data.get("court") if isinstance(data.get("court"), dict) else {}
    kind = str(raw_court.get("court") or "").strip().lower()
    if kind in COURTS:
        matched = _match(raw_court.get("citation"), by_norm) if raw_court.get("citation") else None
        quote = str(raw_court.get("limit_quote") or "").strip()
        court = {"court": kind, "court_label": COURTS[kind], "why": str(raw_court.get("why") or "").strip()[:600],
                 "citation": _cite_view(matched[0]) if matched else None,
                 "limit": quote[:600] if matched and quote and _in_text(quote, matched[0]) else None}
        if kind != "unknown" and not matched:
            court["note"] = "Check with the court clerk which court handles this; no verified section confirmed it."
    for item in data.get("deadlines") or []:
        matched = _match(item.get("citation"), by_norm) if isinstance(item, dict) else None
        quote = str(item.get("quote") or "").strip() if isinstance(item, dict) else ""
        if not matched or not _in_text(quote, matched[0]):
            dropped += 1; continue
        deadlines.append({"title": str(item.get("title") or "Deadline").strip()[:200], "quote": quote[:800], "citation": _cite_view(matched[0])})
    for item in data.get("evidence") or []:
        text = str(item or "").strip()
        if text and not is_evasion(text):
            evidence.append(text[:300])
    for key, out, need_cite in (("weak_spots", weak, True), ("low_cost_paths", paths, False)):
        for item in data.get(key) or []:
            if not isinstance(item, dict):
                dropped += 1; continue
            title = str(item.get("title") or "").strip(); expl = str(item.get("explanation") or "").strip()
            raw_cites = [c for c in (item.get("citations") or []) if str(c).strip().lower() not in ("", "none", "exact or none")] if isinstance(item.get("citations"), list) else []
            matched = _match(raw_cites, by_norm) if raw_cites else ([] if not need_cite else None)
            side = str(item.get("side") or "you").strip().lower()
            if not expl or matched is None or is_evasion(title + " " + expl) or (key == "weak_spots" and side not in SIDES):
                dropped += 1; continue
            row = {"title": (title or "Option")[:200], "explanation": expl[:1500], "citations": [_cite_view(h) for h in matched]}
            if key == "weak_spots":
                row.update(side=side, side_label=SIDES[side])
            out.append(row)
    return {"claims": claims, "court": court, "deadlines": deadlines, "evidence": evidence[:12],
            "weak_spots": weak, "low_cost_paths": paths}, dropped


def _base(situation: str, emergency: bool) -> dict:
    return {"situation": situation, "estimate_note": ESTIMATE_NOTE, "disclaimer": DISCLAIMER,
            "emergency": EMERGENCY if emergency else None, "refused": False, "message": None,
            "claims": [], "court": None, "deadlines": [], "evidence": [], "weak_spots": [], "low_cost_paths": [],
            "help_resources": HELP_RESOURCES, "authorities": [], "lawyer_take": None, "dropped_items": 0,
            "grounded_authority_count": 0}


def analyze_civil_check(situation: str, ask_ai, db=None, *, case_summary: str | None = None, lookup=None) -> dict:
    situation = (situation or "").strip()
    if not situation:
        raise ValueError("Describe the dispute to check it.")
    if len(situation) > MAX_SITUATION_CHARS:
        raise ValueError(f"Description is too long ({MAX_SITUATION_CHARS} characters or fewer).")
    result = _base(situation, is_emergency(situation))
    if is_evasion_request(situation) or re.search(r"(?i)\b(hide|move|transfer)\s+(my\s+)?(money|assets|property)\b.{0,40}\b(judgment|ex|wife|husband|creditor|divorce)", situation):
        return {**result, "refused": True, "message": REFUSAL}
    lookup = lookup or (lambda sections: lookup_sections(db, sections))
    raw = _parse_obj(ask_ai(_candidate_prompt(situation, case_summary)))
    proposed = raw.get("sections") if isinstance(raw.get("sections"), list) else []
    sections = [s for s in (normalize_section(x) for x in proposed[:MAX_CANDIDATES]) if s]
    sections += [s for s in topic_sections(situation) if s not in sections]
    verified = _verified_hits({"hits": lookup(sections + [s for s in BASE_SECTIONS if s not in sections])})
    topical = [h for h in verified if normalize_section(h.get("citation")) in sections]
    if not topical:
        return {**result, "message": NONE_FOUND, "authorities": [_cite_view(h) for h in verified],
                "grounded_authority_count": len(verified)}
    data = _parse_obj(ask_ai(_analysis_prompt(situation, case_summary, _authority_context(topical + [h for h in verified if h not in topical], excerpt_chars=CHECK_EXCERPT_CHARS))))
    kept, dropped = validate_civil_check(data, verified)
    take = validate_lawyer_take(data.get("lawyer_take"), verified)
    if take and is_evasion(take["text"]):
        take = None
    result = with_amendment_note(result, verified)
    return {**result, **kept, "message": None if kept["claims"] else NONE_FOUND, "lawyer_take": take,
            "authorities": [_cite_view(h) for h in _used(verified, kept, take)], "dropped_items": dropped,
            "grounded_authority_count": len(verified)}


def _used(verified, kept, take):
    """Only the verified authorities the kept analysis actually cites."""
    blob = _json.dumps([kept, take], default=str)
    return [h for h in verified if used_in_text(h, blob)]


def civil_check_note_text(result: dict) -> str:
    lines = ["CIVIL CASE CHECK (estimate)", result.get("estimate_note") or "", "", "Dispute: " + (result.get("situation") or "")]
    if result.get("claims"):
        lines.append("\nLIKELY CLAIMS AND DEFENSES")
        lines += [f"- [{c['side_label']}] {c['claim']} ({c['citation']['citation']})" for c in result["claims"]]
    if result.get("court"):
        c = result["court"]; lines.append(f"\nCOURT: {c['court_label']}" + (f" — \"{c['limit']}\"" if c.get("limit") else ""))
    if result.get("deadlines"):
        lines.append("\nDEADLINES"); lines += [f"- {d['title']}: \"{d['quote']}\" ({d['citation']['citation']})" for d in result["deadlines"]]
    if result.get("evidence"):
        lines.append("\nEVIDENCE TO GATHER"); lines += [f"- {e}" for e in result["evidence"]]
    for key, label in (("weak_spots", "WEAK SPOTS"), ("low_cost_paths", "LOWEST-COST PATHS")):
        if result.get(key):
            lines.append("\n" + label)
            lines += [f"- {d['title']}: {d['explanation']}" + (f" [{', '.join(c['citation'] for c in d['citations'])}]" if d['citations'] else "") for d in result[key]]
    if result.get("lawyer_take"):
        lines += ["\nIF I WAS YOUR LAWYER, I WOULD SAY", result["lawyer_take"]["text"]]
    if result.get("message"):
        lines += ["", result["message"]]
    lines += ["", result.get("disclaimer") or ""]
    return "\n".join(lines)[:20000]
