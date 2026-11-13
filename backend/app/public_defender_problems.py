"""Georgia guide: 'Problem with my public defender?'

Legal information, not legal advice. Statutes cited here were confirmed in the
app's law database on 2026-11-13. Case citations used in the guide were confirmed
present in the app's case database where noted in tests. Do not invent a formal
GPDC 'client complaint form'; published GPDC/Georgia.gov contacts are used instead.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from . import language as lang

HEADING = "Problem with my public defender?"
MOTION_KEY = "discharge_appointed_counsel"

_HERE = Path(__file__).resolve().parent
_CANDIDATES = (
    _HERE / "data" / "public_defender_problems.json",
    _HERE.parents[1] / "config" / "public_defender_problems.json",
    _HERE.parents[2] / "config" / "public_defender_problems.json",
    _HERE.parents[2] / "src" / "publicDefenderProblemsData.json",
)

# Counsel the person already has (appointed / public defender / "my lawyer" in a distrust setting).
_COUNSEL = (
    r"\b(public defender|p\.?\s*d\.?\b|court[- ]appointed|appointed (counsel|lawyer|attorney)|"
    r"defensor p[uú]blico|abogado asignado)\b"
)
_MY_LAWYER = r"\b(my|nuestro|mi) (lawyer|attorney|counsel|abogado|abogada|defensor)\b"

# Distrust / "working with the State" and related time-to-act facts.
_DISTRUST = (
    r"(work(?:ing|s)? (with|for|against)|working against|"
    r"with the (state|da|d\.a\.|prosecutor|prosecution|district attorney)|"
    r"on the (state|prosecutor)'s side|against me|"
    r"not (helping|working for) me|won't help|doesn't help|"
    r"won'?t (call|meet|visit|see|talk|review|look)|"
    r"never (call|called|meet|met|visit|visited|came|showed|review)|"
    r"doesn'?t (call|meet|visit|return|review|listen)|"
    r"ignor(?:e|ing|ed) (my )?(witness|evidence|proof|papers?|documents?)|"
    r"pressur(?:e|ing|ed) .{0,40}plea|force(?:d|ing)? me to plea|push(?:ing|ed)? (me )?to plea|"
    r"plea without (explain|telling|going over)|wants? me to (just )?plea|"
    r"missed (a |the )?(deadline|motion|court|hearing)|didn'?t file|"
    r"conflict of interest|represents? (a |my )?co-?defendant|"
    r"contradict(?:s|ed|ing)? the (record|papers|file|evidence)|"
    r"lying to me|lied to me|ineffective|bad lawyer|"
    r"fire (my|him|her|them|the) (lawyer|attorney|public defender|counsel)|"
    r"get (a |me )?(new|different|another) (lawyer|attorney|public defender|counsel)|"
    r"working with the state|del lado (del estado|de la fiscal[ií]a)|"
    r"no me (ayuda|ayuda|llama|atiende)|quiere que me declare)"
)

# "How do I get a public defender?" should not open this problems guide by itself.
_REQUEST_ONLY = re.compile(
    r"(how do i (get|ask for|request)|i need|can i (get|have)|qualify for|apply for).{0,40}"
    r"(public defender|appointed (counsel|lawyer|attorney))",
    re.I,
)

# Post-conviction cues so AI answers can pin habeas / appeal statutes.
_CONVICTED = re.compile(
    r"\b(convict(?:ed|ion)|found guilty|sentenc(?:ed|ing)|after (my|the) trial|"
    r"motion for new trial|habeas|on appeal|my appeal)\b",
    re.I,
)


def _path() -> Path:
    for p in _CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError("public_defender_problems.json was not found")


@lru_cache(maxsize=1)
def catalog() -> dict:
    return json.loads(_path().read_text(encoding="utf-8"))


def _q(text: str) -> str:
    from .civil_topics import current_question
    return current_question(text or "")


def detect(text: str | None) -> bool:
    """True when the user describes distrust of a public defender or court-appointed lawyer.

    Also treats 'my lawyer' plus clear distrust in a criminal public-defense setting,
    but ignores a plain request for appointed counsel.
    """
    q = _q(text or "")
    if not q or _REQUEST_ONLY.search(q) and not re.search(_DISTRUST, q, re.I):
        return False
    has_counsel = bool(re.search(_COUNSEL, q, re.I) or re.search(_MY_LAWYER, q, re.I))
    if not has_counsel:
        return False
    if re.search(_DISTRUST, q, re.I):
        return True
    # 'my public defender is working with the state' and close paraphrases.
    if re.search(_COUNSEL, q, re.I) and re.search(
        r"\b(state|prosecutor|prosecution|da\b|d\.a\.|district attorney|against)\b", q, re.I
    ):
        return True
    return False


def is_primary(text: str | None) -> bool:
    """The question is mainly about the appointed lawyer, not a separate defense-plan request."""
    q = _q(text or "")
    if not detect(q):
        return False
    if re.search(r"\b(build (my|a) defense|defense plan|how do i (fight|defend|beat))\b", q, re.I):
        return False
    # If they name a charge but the focus is the lawyer, still primary.
    return True


def is_post_conviction(text: str | None) -> bool:
    return bool(_CONVICTED.search(_q(text or "")))


# Sections the retriever should try to pin when this guide is triggered.
PINNED_SECTIONS = ("17-12-1", "17-12-22", "17-12-23", "17-7-110")
POST_SECTIONS = ("5-5-40", "5-6-38", "9-14-42", "40-13-33")


def pinned_citations(text: str | None) -> tuple[str, ...]:
    cites = list(PINNED_SECTIONS)
    if is_post_conviction(text) or not text:
        cites.extend(POST_SECTIONS)
    return tuple(cites)


def _pick(item: dict, language: str, en_key: str = "en", es_key: str = "es") -> str:
    spanish = lang.is_spanish(language)
    if spanish:
        return str(item.get(es_key) or item.get(en_key) or "").strip()
    return str(item.get(en_key) or "").strip()


def guide(language: str = "en") -> dict:
    """Skimmable guide pack: quick answer, tappable sections, templates, links."""
    data = catalog()
    code = lang.normalize_language(language)
    spanish = code == "es"
    sections = []
    for spec in data["sections"]:
        items = []
        for item in spec.get("items") or []:
            text = _pick(item, code)
            if text:
                items.append(text)
        sections.append({
            "id": spec["id"],
            "title": spec["title_es"] if spanish else spec["title_en"],
            "items": items,
        })
    templates = []
    for row in data["templates"]:
        templates.append({
            "id": row["id"],
            "kind": row.get("kind") or "letter",
            "motion_key": row.get("motion_key") or None,
            "title": row["title_es"] if spanish else row["title_en"],
            "body": row["body_es"] if spanish else row["body_en"],
        })
    links = []
    for row in data.get("links") or []:
        links.append({
            "id": row["id"],
            "label": row["label_es"] if spanish else row["label_en"],
            "url": row["url"],
        })
    return {
        "title": data["title_es"] if spanish else data["title_en"],
        "hint": data["hint_es"] if spanish else data["hint_en"],
        "language": code,
        "quick": data["quick_es"] if spanish else data["quick_en"],
        "sections": sections,
        "templates": templates,
        "links": links,
        "motion_key": MOTION_KEY,
        "disclaimer": data["disclaimer_es"] if spanish else data["disclaimer_en"],
        "notice": lang.notice(code),
        "heading": HEADING,
    }


def as_text(pack: dict, *, include_templates: bool = True) -> str:
    spanish = pack.get("language") == "es"
    quick_label = "Respuesta rápida" if spanish else "Quick answer"
    lines = [pack.get("title") or HEADING, "", quick_label, pack.get("quick") or ""]
    for section in pack.get("sections") or []:
        items = section.get("items") or []
        if not items:
            continue
        lines.extend(["", section.get("title") or ""])
        lines.extend("• " + item for item in items)
    if include_templates:
        tmpl_label = "Plantillas" if spanish else "Templates"
        for tmpl in pack.get("templates") or []:
            lines.extend(["", tmpl_label + ": " + (tmpl.get("title") or ""), tmpl.get("body") or ""])
    lines.extend(["", pack.get("disclaimer") or "", pack.get("notice") or lang.NOTICE_EN])
    return "\n".join(lines).strip() + "\n"


def answer_section(language: str = "en") -> str:
    """Compact section inserted into AI answers and defense plans. English heading (app style)."""
    data = catalog()
    code = lang.normalize_language(language)
    spanish = code == "es"
    quick = data["quick_es"] if spanish else data["quick_en"]
    bullets = data["compact_ladder_es"] if spanish else data["compact_ladder_en"]
    lines = [HEADING, "• " + quick]
    lines.extend("• " + b for b in bullets)
    return "\n".join(lines)


def follow_ups(language: str = "en") -> list[dict]:
    spanish = lang.is_spanish(language)
    if spanish:
        return [
            {"question": "¿Qué debo escribirle a mi defensor público?",
             "why": "Una carta con fecha crea un registro y es el primer paso."},
            {"question": "¿Cuándo puedo pedirle al juez un abogado nuevo?",
             "why": "El juez busca una causa justificada, como un conflicto o una ruptura total de la comunicación."},
            {"question": "¿Cómo presento una queja sin perder a mi abogado en el caso?",
             "why": "Una queja ante el Colegio de Abogados no saca al abogado de su caso."},
        ]
    return [
        {"question": "What should I write to my public defender?",
         "why": "A dated letter creates a record and is the first step."},
        {"question": "When can I ask the judge for a new lawyer?",
         "why": "The judge looks for good cause, such as a conflict or a complete breakdown in communication."},
        {"question": "How do I file a complaint without getting the lawyer taken off my case?",
         "why": "A State Bar grievance does not remove the lawyer from your case."},
    ]


def _section_bounds(text: str, start: int) -> int:
    from .answer_format import _KNOWN_HEADINGS
    lines = text[start:].splitlines()
    # first line is the heading
    offset = len(lines[0]) + 1 if lines else 0
    pos = start + offset
    for line in lines[1:]:
        s = line.strip()
        if s and (s.lower().rstrip(":") in _KNOWN_HEADINGS or s.startswith("Note:")) and s.lower().rstrip(":") != HEADING.lower():
            return pos
        pos += len(line) + 1
    return len(text)


def attach(analysis: str, question: str, language: str = "en") -> tuple[str, bool]:
    """Insert or replace the guide section when the user's words trigger it."""
    if not detect(question):
        return analysis or "", False
    section = answer_section(language)
    text = analysis or ""
    head = re.compile(r"(?im)^\s*" + re.escape(HEADING) + r"\s*:?\s*$")
    m = head.search(text)
    if m:
        end = _section_bounds(text, m.start())
        text = (text[:m.start()].rstrip() + "\n\n" + section + "\n\n" + text[end:].lstrip()).strip()
    else:
        # After Quick answer if present; otherwise after a leading title line; else at the top.
        qa = re.search(r"(?im)^\s*quick answer\s*:?\s*$", text)
        if qa:
            end = _section_bounds(text, qa.start())
            text = text[:end].rstrip() + "\n\n" + section + "\n\n" + text[end:].lstrip()
        else:
            text = section + ("\n\n" + text.strip() if text.strip() else "")
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text, True


def prompt_block(question: str) -> str:
    if not detect(question):
        return ""
    extra = ""
    if is_post_conviction(question):
        extra = (
            " They may already have a conviction, so also mention the short deadlines for a motion for new trial "
            "(generally 30 days, O.C.G.A. § 5-5-40), a notice of appeal (generally 30 days, O.C.G.A. § 5-6-38), "
            "and habeas corpus (generally 4 years for a felony and 1 year for a misdemeanor under O.C.G.A. § 9-14-42(c), "
            "and 180 days for a misdemeanor traffic conviction under O.C.G.A. § 40-13-33) — only if those laws are listed."
        )
    return (
        "The user is worried their public defender or court-appointed lawyer is not working for them. "
        "Lead with a short Quick answer, then give clear options in this order: (1) document everything and write the lawyer "
        "to request a meeting; (2) contact the circuit public defender or a supervisor and ask for reassignment; "
        "(3) a motion asking the judge to discharge appointed counsel and appoint a different lawyer — they generally cannot "
        "pick a particular appointed lawyer and must show good cause such as a conflict of interest or a complete breakdown "
        "in communication; the judge may deny the request and they could end up self-represented or delayed; "
        "(4) hire a private criminal-defense lawyer if they can (Georgia legal aid is generally civil, not criminal); "
        "(5) contact GPDC to reach the office, and/or file a State Bar grievance or call the Client Assistance Program — "
        "a grievance does not remove the lawyer from the case or stop court dates; "
        "(6) after a conviction only, ineffective assistance under Strickland is usually raised in a motion for new trial, "
        "an appeal, or habeas, which have short deadlines. "
        "Cite only listed laws. Do not invent a formal GPDC complaint form. Do not say a grievance fires the lawyer. "
        "Do not treat disagreements over strategy alone as enough to require a new appointed lawyer. "
        "This is legal information, not legal advice."
        + extra
    )


def merge_follow_ups(existing: list | None, question: str, language: str = "en") -> list[str]:
    if not detect(question):
        return list(existing or [])
    have = [q for q in (existing or []) if q]
    seen = {q.lower() for q in have}
    for item in follow_ups(language):
        q = item["question"]
        if q.lower() not in seen:
            have.append(q)
            seen.add(q.lower())
    return have[:6]


def merge_follow_up_details(existing: list | None, question: str, language: str = "en") -> list[dict]:
    if not detect(question):
        return list(existing or [])
    out = list(existing or [])
    seen = {str(x.get("question") or "").lower() for x in out if isinstance(x, dict)}
    for item in follow_ups(language):
        if item["question"].lower() not in seen:
            out.append(item)
            seen.add(item["question"].lower())
    return out[:6]
