"""Defense-first help for criminal questions.

The app exists to help people understand how a criminal case can be defended. This module:
- detects broad "how do I defend this case" questions and other criminal questions (current question only),
- picks the Georgia Code sections to retrieve for them (looked up by exact citation; anything not in the
  law database or not verified is dropped by the normal verified-hit filter),
- keeps self-defense statutes out of broad defense answers unless the user mentions force,
- adds prompt guidance so answers are direct and defense-oriented,
- builds a deterministic "Motions that could help" section from the app's motion library (motions.py),
  citing only sections that were found and verified in the database.
Nothing here assumes custody, a conviction, or who is asking.
"""
from __future__ import annotations
import logging
import re

_log = logging.getLogger(__name__)

MOTIONS_HEADING = "Motions that could help"

_CIVIL = r"\b(evict|dispossessory|landlord|tenant|lease|rent\b|deposit|debt|collector|garnish|divorce|custody|visitation|child support|alimony|small claims|sued|lawsuit|being sued|foreclos|probate|contract|insurance claim|workers'? comp)"
_SELF_DEFENSE = r"self[- ]?defen[cs]e|stand (my|your|their|his|her) ground|defend(ing|ed)? (my ?self|him ?self|her ?self|them ?selves|themselves|someone|my (family|kids?|child))|protect(ing|ed)? (my ?self|him ?self|her ?self)|immunity hearing"
_FORCE = r"\b(fight|fought|hit|punch|shot|shoot|stab|attack|assault|battery|force|weapon|gun|knife|kill|murder|manslaughter|hurt (him|her|them|someone))"
# "help my defense", "best defense for a theft charge", "how do I beat this case", "fight the charges" ...
_BROAD = (r"(?<!self )(?<!self-)\bdefen[cs]es?\b(?! (attorney|lawyer|fund|department|contract|budget))"
          r"|\b(beat|fight|win|defend|beating|fighting) (the|my|this|a|his|her|their|our) (case|charges?|ticket)"
          r"|\b(get|getting) (the|my|this|his|her|their) (case|charges?) (dropped|dismissed|thrown out|reduced)"
          r"|\bhelp (my|the|his|her|their) case\b")
CRIMINAL = (r"\b(arrest|charged?|charges|crime|criminal|indict|accus(ed|ation)|arraign|plea|misdemeanor|felony|prosecut|district attorney|\bda\b|"
            r"warrant|bond|bail|police|detectives?|cops?|officers?|probation|theft|shoplift|robbery|burglary|drugs?|marijuana|possession|assault|battery|dui|"
            r"under the influence|murder|manslaughter|trespass|disorderly|obstruction|fraud|forgery|stolen|weapon|firearm|"
            r"public defender|court date|first offender|suppress|speedy trial|discovery|convict|found guilty|sentenc|new trial|habeas|appeal|"
            r"expung|record restrict|criminal record|pardon|parole|probation)")


def _q(text: str) -> str:
    from .civil_topics import current_question
    return current_question(text or "").lower()


def is_self_defense(question: str) -> bool:
    return bool(re.search(_SELF_DEFENSE, _q(question)))


def mentions_force(question: str) -> bool:
    q = _q(question)
    return bool(re.search(_FORCE, q) or re.search(_SELF_DEFENSE, q))


def is_broad_defense(question: str) -> bool:
    """A general 'what could help my defense / how do I fight this case' question (not self-defense, not civil)."""
    q = _q(question)
    if not q or re.search(_CIVIL, q) or re.search(_SELF_DEFENSE, q):
        return False
    return bool(re.search(_BROAD, q))


def is_criminal(question: str) -> bool:
    q = _q(question)
    if not q:
        return False
    if is_broad_defense(q):
        return True
    return bool(re.search(CRIMINAL, q)) and not (re.search(_CIVIL, q) and not re.search(r"\b(arrest|charged|criminal|crime|felony|misdemeanor)", q))


# Georgia Code sections behind each defense avenue. All confirmed present in the law database on
# 2026-11-12 (Code text is the 2022 edition); at answer time they are still re-checked and dropped
# unless found and verified.
BROAD_DEFENSE_SECTIONS: tuple[str, ...] = (
    "17-5-30",   # motion to suppress illegally seized evidence
    "24-8-824",  # only voluntary confessions admissible
    "17-16-4",   # discovery: what the prosecution must disclose
    "17-7-170",  # demand for speedy trial
    "17-3-1",    # time limits for prosecution
    "17-7-110",  # time for filing pretrial motions
    "16-3-20",   # justification (general)
    "16-3-25",   # entrapment
    "16-3-5",    # mistake of fact
    "16-3-2",    # mental capacity
    "17-16-5",   # alibi witnesses (notice)
    "42-8-60",   # First Offender
    "16-13-2",   # conditional discharge (first drug possession)
    "15-1-15",   # drug court (accountability court)
)
CRIMINAL_CORE_SECTIONS: tuple[str, ...] = ("17-5-30", "17-16-4", "17-7-170", "42-8-60")
# Use-of-force statutes: only relevant when the question involves force or self-defense.
SELF_DEFENSE_FAMILY = {"16-3-21", "16-3-23", "16-3-23.1", "16-3-24", "16-3-24.1", "16-3-24.2", "16-3-28"}
_SEC = re.compile(r"\b\d{1,2}-\d{1,3}-\d+(?:\.\d+)?\b")


def defense_sections(question: str) -> list[str]:
    q = _q(question)
    if is_broad_defense(q):
        out = list(BROAD_DEFENSE_SECTIONS)
        if re.search(r"\b(dui|under the influence)", q):
            out.remove("16-13-2")
        return out
    if is_criminal(q) and _allowed_stages(q) == _PRE:
        out = list(CRIMINAL_CORE_SECTIONS)
        if re.search(r"\b(drugs?|marijuana|weed|possession|cocaine|meth|pills|controlled substance)", q):
            out.append("16-13-2")
        return out
    return []


def context_limit(question: str, default: int) -> int:
    if is_broad_defense(question):
        return max(default, 14)
    if is_criminal(question):
        return max(default, 10)
    return default


def _secs(hit: dict) -> list[str]:
    return _SEC.findall(str(hit.get("citation") or ""))


def drop_off_topic(hits: list[dict], question: str, trusted: set) -> list[dict]:
    """Broad defense question with no force involved: keep out the use-of-force statutes and untrusted
    full-text matches (e.g. anything titled 'defense'), so the answer isn't one statute family."""
    if not is_broad_defense(question):
        return hits
    force = mentions_force(question)
    out = []
    for h in hits:
        secs = _secs(h)
        if not force and any(s in SELF_DEFENSE_FAMILY for s in secs):
            continue
        if h.get("corpus") == "persisted_authorities" and secs and not any(s in trusted for s in secs):
            continue
        out.append(h)
    return out


def defense_hits(db, question: str, retrieval: dict, limit: int = 14) -> dict:
    """Merge exact-citation defense sections into the retrieval (topic/charge hits stay first)."""
    sections = defense_sections(question)
    if not sections or db is None:
        return retrieval
    from .charge_check_service import lookup_sections
    try:
        with db.begin_nested():
            found = lookup_sections(db, sections)
    except Exception as exc:  # never fail an answer because of this lookup
        _log.warning("Defense citation lookup skipped: %s", type(exc).__name__)
        return retrieval
    for h in found:
        h.pop("full_text", None)
        h["excerpt"] = (h.get("excerpt") or "")[:900]
    have = {str(h.get("citation") or "").lower() for h in retrieval.get("hits", [])}
    extra = [h for h in found if str(h.get("citation") or "").lower() not in have]
    hits = list(retrieval.get("hits", []))
    if is_broad_defense(question):
        hits = extra + hits
    else:
        hits = hits[:6] + extra + hits[6:]
    return {**retrieval, "hits": hits[:limit]}


# ---------------------------------------------------------------- prompt guidance
DIRECT = ("Be direct and concrete: lead with the points that help most with this exact question. For every law, "
          "defense, motion, or option you mention, say in plain words how it can help and when it applies (for example "
          "'This may help if ...'); do not just restate what a statute says. Cut filler, generic warnings, and anything "
          "not about the question.")

DEFENSE_FOCUS = ("DEFENSE FOCUS: this app exists to help people understand how a criminal case can be defended. For this "
                 "criminal question, after briefly explaining what applies, emphasize the defense angles that fit it: what the "
                 "State has to prove and which parts could be contested; how evidence may be challenged (an unlawful stop or "
                 "search, statements to police, identification, witness credibility, chain of custody); rights and procedure "
                 "(a lawyer or public defender, discovery, a speedy trial demand, time limits for prosecution); defenses that "
                 "may apply ('may apply if ...'); and options that can lessen the outcome (First Offender, conditional "
                 "discharge for a first drug possession, accountability courts, plea negotiations). Include only angles that "
                 "genuinely fit this question and never assume facts the user did not give. The app adds a separate "
                 "'" + MOTIONS_HEADING + "' section itself, so do not write that heading.")

BROAD_DEFENSE = ("BROAD DEFENSE QUESTION: the user is asking in general what could help a criminal defense. Under Short "
                 "answer, say in 1-2 sentences that the strongest defense depends on the charge and the facts, and invite "
                 "them to share the charge and where the case stands so the answer can be more specific. Under How it "
                 "works in Georgia give an organized overview with these group labels, each on its own line ending with ':' "
                 "and followed by 1-3 '- ' bullets: 'Challenging the evidence:' (illegal stop or search and a motion to "
                 "suppress, statements to police, identification, witness credibility, chain of custody); 'Rights and court "
                 "procedure:' (lawyer or public defender, discovery of the prosecution's evidence, speedy trial demand, time "
                 "limits for prosecution); 'Defenses that may apply:' (justification, entrapment, mistake of fact, mental "
                 "capacity, alibi, each as 'may apply if ...' in one line; only mention self-defense as one example of "
                 "justification); 'Ways to lessen the outcome:' (First Offender, conditional discharge for a first drug "
                 "possession, accountability courts, plea negotiations); 'Information to gather for your lawyer:' (witness "
                 "names, texts, photos, video, receipts, records, a written timeline). Cite the listed laws where they fit. "
                 "This answer may run up to about 450 words.")


AFTER_CONVICTION = ("DEFENSE FOCUS (after a conviction, on probation, or about a record): emphasize the remedies that fit "
                    "this question and could undo a conviction, reduce time, end supervision sooner, or clear a record, saying "
                    "plainly how each can help and when it applies. Never assume the person is in custody unless the user says so. "
                    "The app adds a separate '" + MOTIONS_HEADING + "' section itself, so do not write that heading.")


def prompt_block(question: str) -> str:
    if is_broad_defense(question):
        return DEFENSE_FOCUS + " " + BROAD_DEFENSE
    if is_criminal(question):
        return DEFENSE_FOCUS if _allowed_stages(_q(question)) == _PRE else AFTER_CONVICTION
    return ""


def max_words(question: str) -> int:
    return 560 if is_broad_defense(question) else (480 if is_criminal(question) else 420)


# ---------------------------------------------------------------- lawyer questions and follow-ups
BROAD_LAWYER_QUESTIONS = (
    "Based on the charge and the evidence, which defenses or motions fit this case best?",
    "Was any stop, search, or statement to police handled in a way that could be challenged?",
    "What evidence does the prosecution have, and when will we see it through discovery?",
    "Would a speedy trial demand help here, or is there a reason to wait?",
    "Could First Offender, conditional discharge, an accountability court, or a plea agreement be an option?",
)
CHARGE_FOLLOW_UPS = (
    "What defenses could fit this charge in Georgia?",
    "How does a motion to suppress evidence work in Georgia?",
    "Who qualifies for First Offender treatment in Georgia?",
)
BROAD_FOLLOW_UPS = (
    "How does a motion to suppress evidence work in Georgia?",
    "How do I demand a speedy trial in Georgia?",
    "Who qualifies for First Offender treatment in Georgia?",
)


# ---------------------------------------------------------------- motions
# Structured catalog: app/data/ga_criminal_motions.json (built by scripts/build_ga_criminal_motions.py).
import json as _json
from functools import lru_cache as _lru_cache
from pathlib import Path as _Path

CATALOG_PATH = _Path(__file__).with_name("data") / "ga_criminal_motions.json"
_PRE = {"arrested", "pretrial", "plea", "trial"}
_POST_STAGES = {"sentenced", "appeal", "prison", "probation", "record"}
_POST = r"\b(convicted|found guilty|sentenced|verdict|after (the )?trial|appeal|habeas|new trial|in prison|serving (a |my |his |her )?(sentence|time)|parole)\b"
_PROBATION = r"\bprobation|\bvop\b"
_RECORD = r"expung|record restrict|clear (my|his|her) record|criminal record|pardon"
MAX_MOTIONS = 5
MAX_BROAD_MOTIONS = 6


@_lru_cache(maxsize=1)
def catalog() -> tuple[dict, ...]:
    with open(CATALOG_PATH, encoding="utf-8") as fh:
        data = _json.load(fh)
    return tuple(data["motions"])


def catalog_by_key() -> dict:
    return {m["key"]: m for m in catalog()}


def _allowed_stages(q: str) -> set:
    allowed = set()
    if re.search(_POST, q):
        allowed |= {"sentenced", "appeal", "prison"}
    if re.search(_PROBATION, q):
        allowed |= {"probation", "sentenced"}
    if re.search(_RECORD, q):
        allowed |= {"record"}
    if not allowed:
        allowed = set(_PRE)
    return allowed


def motion_keys(question: str, max_items: int | None = None) -> list[str]:
    """Catalog motions relevant to the current question, most relevant first."""
    q = _q(question)
    if not is_criminal(q):
        return []
    allowed = _allowed_stages(q)
    fits = [m for m in catalog() if set(m["stages"]) & allowed]
    keys = [m["key"] for m in fits if m["triggers"] and re.search(m["triggers"], q)]
    if is_broad_defense(q):
        keys += [m["key"] for m in fits if m["broad_defense"]]
        cap = max_items or MAX_BROAD_MOTIONS
    else:
        if len(keys) < 2 and allowed == _PRE:  # defense-first: always offer the core pretrial motions
            keys += [m["key"] for m in fits if m["default_criminal"]]
        cap = max_items or MAX_MOTIONS
    return list(dict.fromkeys(keys))[:cap]


def suggested_motions(question: str, lookup) -> list[dict]:
    """Relevant catalog motions with only verified Georgia citations attached.
    ``lookup(citations) -> verified hit dicts`` (O.C.G.A. section numbers or full court-rule citations).
    A motion whose Georgia sections can't be verified is dropped; case-law-only motions are kept without a citation;
    'unverified_authority' is never shown."""
    keys = motion_keys(question)
    if not keys:
        return []
    by_key = catalog_by_key()
    wanted = list(dict.fromkeys(c for k in keys for c in by_key[k]["ocga"] + by_key[k]["court_rules"]
                                + ([by_key[k]["deadline_source"]] if by_key[k].get("deadline_source") else [])))
    try:
        hits = lookup(wanted) or [] if wanted else []
    except Exception as exc:
        _log.warning("Motion citation lookup skipped: %s", type(exc).__name__)
        return []
    verified = {}
    for h in hits:
        cite = str(h.get("citation") or "")
        verified.setdefault(cite, h)
        for sec in _secs(h):
            verified.setdefault(sec, h)
    out = []
    for k in keys:
        m = by_key[k]
        sec_hits = [verified[s] for s in m["ocga"] if s in verified]
        rule_hits = [verified[r] for r in m["court_rules"] if r in verified]
        if m["ocga"] and not sec_hits:
            continue  # its Georgia law couldn't be verified right now
        shown = (sec_hits[:2] + rule_hits[:1]) if sec_hits else rule_hits[:1]
        src = m.get("deadline_source")
        deadline = m.get("deadline") if (src is None and rule_hits) or (src and src in verified) else None
        out.append({"key": k, "title": m["name"], "purpose": m["purpose"], "how_it_helps": m["how_it_helps"],
                    "when_it_applies": m["when_it_applies"], "goal": m["goal"], "timing": deadline,
                    "stages": list(m["stages"]), "template_key": m.get("template_key"),
                    "draftable": bool(m.get("template_key")), "citations": [str(h.get("citation")) for h in shown],
                    "authorities": shown})
    return out


def motions_section(motions: list[dict], has_case_stage: bool) -> str:
    if not motions:
        return ""
    lines = [MOTIONS_HEADING]
    for m in motions:
        cites = ", ".join(motions_cite_label(c) for c in m["citations"])
        head = f"{m['title']} ({cites})" if cites else m["title"]
        timing = f" Timing: {m['timing']}" if m.get("timing") else ""
        lines.append(f"• {head}: {m['purpose']} {m['when_it_applies']} How it can help: {m['how_it_helps']}{timing}")
    if has_case_stage and any(m["draftable"] for m in motions):
        lines.append("• Tap \"Open My Case\" below to see motions for your case stage and draft a fill-in-the-blank version to review with a lawyer.")
    lines.append("• A lawyer should decide whether and when to file any motion; deadlines can be short.")
    return "\n".join(lines)


def motions_cite_label(citation: str) -> str:
    return re.sub(r"\s*\(text as of[^)]*\)", "", str(citation or "")).strip()


def insert_motions(analysis: str, section: str) -> str:
    """Put the motions section right before 'Questions to ask your lawyer' (or before help / the note)."""
    if not section:
        return analysis
    text = str(analysis or "")
    for pat in (r"(?im)^\s*questions to ask your lawyer\s*:?\s*$", r"(?im)^\s*deadlines and costs\s*:?\s*$",
                r"(?im)^\s*where to get help\s*:?\s*$", r"(?m)^\s*Note:"):
        m = re.search(pat, text)
        if m:
            return text[:m.start()].rstrip() + "\n\n" + section + "\n\n" + text[m.start():].lstrip()
    return text.rstrip() + "\n\n" + section


def default_stage(question: str) -> str | None:
    """My Case stage to offer (its 'Draft this motion' buttons) when the question names no stage."""
    q = _q(question)
    if is_broad_defense(q) or (is_criminal(q) and motion_keys(q) and _allowed_stages(q) == _PRE):
        return "pretrial"
    return None


_GROUP_LABEL = re.compile(r"^[A-Z][A-Za-z ,'/&()-]{2,60}:$")


def drop_empty_group_labels(analysis: str) -> str:
    """Remove a group label line ('Ways to lessen the outcome:') left with no bullet under it (e.g. after a cut-off)."""
    lines = str(analysis or "").split("\n")
    out = []
    for i, line in enumerate(lines):
        if _GROUP_LABEL.match(line.strip()):
            nxt = next((x.strip() for x in lines[i + 1:] if x.strip()), "")
            if not nxt or not (nxt.startswith("•") or nxt.startswith("-")):
                continue
        out.append(line)
    return "\n".join(out)
