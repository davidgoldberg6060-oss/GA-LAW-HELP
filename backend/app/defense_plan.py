"""Automatic "Your Defense Plan".

Whenever a user describes their OWN legal situation (a criminal charge, a ticket, probation, a past
conviction, an eviction, a custody case, a debt lawsuit, a job dispute ...), or taps "Build my defense",
AI Help answers with a structured, defense-first plan for THOSE facts instead of a general explainer.
Uploaded case papers (Scan a paper / Read a document) get the same plan, built from what the paper says.

- ``detect(question)`` -> the case type for the current message (or None).
- ``plan_for(question, history)`` -> ``{"status": "build" | "clarify", ...}`` or None (normal answer).
  Too vague (no charge or claim named) -> "clarify": one or two short questions instead of guessing.
- Georgia Code sections for each case type are looked up by exact citation; anything not in the law
  database or not verified is dropped by the normal verified-hit filter, so this list can never add an
  unverified authority. All were confirmed present in the law database on 2026-11-13 (2022 Code text).
Nothing here assumes custody, guilt, or who is asking.
"""
from __future__ import annotations

import re

PLAN_TITLE = "Your Defense Plan"

# ------------------------------------------------------------------ detection
_PERSONAL = (r"\b(i|i'm|im|i've|ive|i'd|my|me|mine|we|we're|our|us|he|he's|she|she's|they|they're|his|her|their|"
             r"son|daughter|husband|wife|boyfriend|girlfriend|brother|sister|mom|mother|dad|father|cousin|uncle|aunt|"
             r"friend|fianc[eé]e?|partner|nephew|niece|grand(son|daughter|ma|pa|mother|father)|kid|child)\b")
_EXPLICIT = (r"\b(build|make|write|create|give|draft|put together|do)\b.{0,20}\bdefen[cs]e( plan)?\b|\bdefen[cs]e plan\b"
             r"|\bbuild my case\b|\bbuild (me )?a case\b")

# Order matters: the first match wins.
TYPES: tuple[tuple[str, str, str, str], ...] = (
    # key, label, family, pattern
    ("probation", "Probation violation", "criminal",
     r"\bprobation (violation|revocation|officer|warrant)|violat\w* (my |his |her |their |the terms of )?(probation|parole)|\bvop\b|revok\w* (my |his |her )?probation"
     r"|\bparole (violation|revocation|officer)|\b(on|while on) (probation|parole)\b"),
    ("post_conviction", "After a conviction", "criminal",
     r"\b(convicted|found guilty|was sentenced|got sentenced|been sentenced|sentenced to|guilty verdict|appeal (my|his|her|the) (conviction|sentence|criminal case)|habeas|new trial"
     r"|expunge?|record restriction|restrict (my|his|her) record|clear (my|his|her) record|seal (my|his|her) record)\b"),
    ("dui", "DUI", "criminal", r"\b(dui|dwi|drunk driving|driving (while )?drunk|under the influence|blood test|breath(alyzer| test)|implied consent|field sobriety|bac)\b"),
    ("drugs", "Drug possession", "criminal",
     r"\b((?<!writ of )(?<!demand for )possession(?! (of (the )?(property|premises|house|home|apartment|unit|car|vehicle)|for\b|and\b|of (my|our|the) (place|home|house|apartment)))|drugs?|marijuana|weed|cocaine|crack|meth|fentanyl|pills|controlled substance|paraphernalia|thc)\b"),
    ("traffic", "Traffic ticket", "criminal",
     r"\b(speeding|speed(ing)? ticket|traffic (ticket|citation|stop)|ran a red light|red light|stop sign|no insurance|driving (on a |with a )?suspended|"
     r"suspended licen[cs]e|no (driver'?s? )?licen[cs]e|without a licen[cs]e|reckless driving|too fast|mph|super speeder|hit and run|failure to yield|"
     r"seat ?belt|expired tag|uniform traffic citation|(got|received|gave me) a (ticket|citation))\b"),
    ("theft", "Theft or shoplifting", "criminal",
     r"\b(shoplift\w*|theft|stole|stealing|stolen|larceny|took (something|items?) from (a |the )?store|walked out (of|with)|loss prevention)\b"),
    ("eviction", "Eviction", "civil",
     r"\b(evict\w*|dispossessory|notice to (vacate|quit)|writ of possession|demand for possession|behind on (my |the |our )?rent|(didn'?t|did not|can'?t|cannot|couldn'?t) pay (my |the |our )?rent|"
     r"non-?payment of rent|unpaid rent|late on (my |the )?rent|(kick|kicking|put|putting|throw|throwing) (me|us) out|lock(ed|ing)? (me|us) out)\b"),
    ("custody", "Custody or family case", "civil",
     r"\b((child|joint|sole|physical|legal|primary|full|shared) custody|custody (of (my|our|the) (kids?|child|children|son|daughter)|order|case|modification|hearing|battle|agreement|arrangement)|"
     r"visitation|parenting (plan|time)|child support|divorce|alimony|legitimat\w*|paternity|modif\w* (the |my |our )?(custody|support|parenting))\b"),
    ("debt", "Debt or collection lawsuit", "civil",
     r"\b(debt|debt collector|collection agency|collections|garnish\w*|credit card (debt|company|bill|lawsuit)|repossess\w*|payday loan|medical bills?|judgment against me)\b"),
    ("employment", "Job or wage dispute", "civil",
     r"\b((got|was|been|getting|being) (fired|terminated|laid off)|fired me|wages?|paycheck|overtime|my (boss|employer|job)|discriminat\w*|harass\w* at work|retaliat\w*|unemployment|final pay)\b"),
    ("criminal", "Criminal charge", "criminal",
     r"\b(battery|assault|aggravated|burglary|robbery|trespass\w*|disorderly|obstruction|resisting|fraud|forgery|identity theft|weapon|firearm|gun|"
     r"murder|manslaughter|homicide|kidnap\w*|stalking|terroristic threats?|family violence|domestic violence|criminal damage|vandalism|"
     r"carjack\w*|elud\w*|fleeing|prostitution|solicitation|child (molest\w*|abuse|cruelty)|cruelty to children|rape|sexual (assault|battery)|riot|affray)\b"),
    ("civil_suit", "Lawsuit", "civil",
     r"\b(sued|suing|lawsuit|small claims|magistrate court).{0,80}\b(accident|wreck|injur\w*|contract|breach|car|deposit|property|damage|loan|money|bill|fence|dog|repairs?|work|business)\b"
     r"|\b(accident|wreck|contract|breach|deposit|damage|loan|repairs?).{0,80}\b(sued|suing|lawsuit|small claims|magistrate court)\b"),
)
_TYPE = {k: (label, family) for k, label, family, _ in TYPES}
# Vague: a case exists but no charge or claim is named.
_VAGUE_CRIMINAL = (r"\b(arrest\w*|charged|charges?|warrant|in jail|locked up|booked|indict\w*|arraign\w*|court date|criminal case|"
                   r"public defender|bond|bail|the police|cops?|detective|got caught|picked up)\b")
_VAGUE_CIVIL = r"\b(sued|suing|lawsuit|served( with)? (papers?|a summons)|summons|complaint|small claims|court papers?|being taken to court)\b"
# A described event ("I got arrested", "my son was charged", "I'm being sued"), not an informational question.
_EVENT = (r"\b(i|we|he|she|they|my \w+|our \w+)( just)?\s?(got|was|were|am|are|is|been|have been|has been|'m|'s|'re|keep getting)( being| just)? "
          r"(arrested|charged|picked up|locked up|booked|indicted|sued|served|taken to court|in jail|caught)\b"
          r"|\b(i|we) (have|got) (a )?(court date|court|warrant|case|charges?|lawsuit)\b|\bthey (arrested|charged|sued) (me|us|him|her|them|my \w+)\b")


def _q(text: str) -> str:
    from .civil_topics import current_question
    return re.sub(r"\s+", " ", current_question(text or "")).strip().lower()


def detect(text: str) -> str | None:
    """Case type named in ``text`` (already the current message), or None."""
    q = str(text or "").lower()
    for key, _label, _family, pat in TYPES:
        if re.search(pat, q):
            return key
    return None


def is_explicit(text: str) -> bool:
    return bool(re.search(_EXPLICIT, _q(text)))


def is_personal(text: str) -> bool:
    return bool(re.search(_PERSONAL, _q(text)))


def _vague_family(q: str) -> str | None:
    if re.search(_VAGUE_CIVIL, q):
        return "civil"
    if re.search(_VAGUE_CRIMINAL, q):
        return "criminal"
    return None


def _earlier_user_text(query: str, conversation) -> str:
    """The user's earlier words: app-wrapped history ('User: ...' lines) plus the server-side thread."""
    from .civil_topics import _WRAPPER_RE
    parts = _WRAPPER_RE.split(str(query or ""))
    earlier = [re.split(r"\n(?:Assistant|AI|STANDALONE ASSISTANT):", p)[0] for p in parts[1:-1]] if len(parts) > 2 else []
    try:
        from . import conversation_memory as _cm
        c = _cm._as_ctx(conversation) if conversation else None
        if c and not _cm.is_empty(c):
            earlier += [t.get("user_text") or "" for t in c["thread"][-4:]]
            other = (c.get("elsewhere") or {}).get("user_text") if isinstance(c.get("elsewhere"), dict) else ""
            if other and not earlier:
                earlier.append(other)
    except Exception:
        pass
    return " ".join(e.strip() for e in earlier if e and e.strip())[-1500:]


def plan_for(query: str, conversation=None, *, force: bool = False) -> dict | None:
    """Decide whether this message gets an automatic Defense Plan.

    ``force``: an uploaded paper (always build or clarify). Returns None for informational questions
    ("how does First Offender work?"), follow-ups that are not a new situation, and general broad
    "what could help a defense" questions (those keep the defense overview)."""
    from .defense_help import is_broad_defense
    q = _q(query)
    if not q:
        return None
    explicit = is_explicit(q)
    kind = detect(q)
    personal = is_personal(q)
    event = bool(re.search(_EVENT, q))
    if not (force or explicit or (personal and kind) or (event and _vague_family(q))):
        return None
    facts = q
    if not kind and (explicit or force):
        earlier = _earlier_user_text(query, conversation).lower()
        k2 = detect(earlier)
        if k2:
            kind, facts = k2, (earlier + " " + q).strip()
    if kind:
        label, family = _TYPE[kind]
        return {"status": "build", "case_type": kind, "label": label, "family": family, "facts": facts}
    if not explicit and not force and is_broad_defense(q):
        return None  # "what could help my defense": keep the broad overview (it invites the charge)
    family = _vague_family(q) or ("civil" if re.search(r"\b(sue|sued|court|landlord|tenant|custody|debt)\b", q) else "criminal")
    return {"status": "clarify", "case_type": None, "label": "", "family": family, "facts": facts,
            "questions": list(CLARIFY[family])}


# ------------------------------------------------------------------ clarify (no model call: never guess)
CLARIFY = {
    "criminal": ("What is the charge? It's on the ticket, warrant, or bond paper.",
                 "Where is the case now: just arrested, court date set, or already sentenced?"),
    "civil": ("What is the case about: eviction, a debt, custody, a job, or something else?",
              "Were you served court papers, and what date is on them?"),
}
CLARIFY_EXAMPLES = {
    "criminal": ("I was charged with DUI after a traffic stop", "I was arrested for possession after a car search",
                 "I have a shoplifting charge, first offense"),
    "civil": ("My landlord filed an eviction for unpaid rent", "I'm being sued over a credit card debt",
              "I want to change our custody order"),
}
_MEANWHILE = {
    "criminal": ("Don't talk about the facts with police, the alleged victim, or on social media.",
                 "Write down what happened now: dates, times, places, and witnesses.",
                 "Keep every paper you got, and never miss a court date."),
    "civil": ("Don't ignore court papers; most have a short deadline to answer.",
              "Write down what happened now, with dates, and save texts, receipts, and letters.",
              "Keep paying what you can and keep proof of every payment."),
}


def clarify_text(plan: dict) -> str:
    fam = plan.get("family") or "criminal"
    q1, q2 = plan["questions"][:2]
    return (f"{PLAN_TITLE}\n\nQuick answer\nI can build your defense plan as soon as I know two things. {q1} {q2}\n\n"
            "While you find that out\n" + "\n".join("• " + x for x in _MEANWHILE[fam]) + "\n\nWhere to get help\n• See below.")


# ------------------------------------------------------------------ law to retrieve per case type
SECTIONS: dict[str, tuple[str, ...]] = {
    "dui": ("40-6-391", "40-6-392", "40-5-67.1", "40-5-67", "17-5-30", "24-8-824", "17-16-4", "17-7-170", "42-8-60"),
    "drugs": ("16-13-30", "17-5-30", "16-13-2", "17-16-4", "24-8-824", "17-7-170", "15-1-15", "42-8-60"),
    "theft": ("16-8-14", "16-8-2", "17-16-4", "24-8-824", "17-7-170", "42-8-60", "35-3-37"),
    "traffic": ("40-6-181", "40-13-3", "40-13-1", "40-5-57", "40-13-58", "17-16-4", "17-7-170"),
    "criminal": ("17-5-30", "24-8-824", "17-16-4", "17-7-170", "17-3-1", "17-6-1", "42-8-60"),
    "probation": ("42-8-34.1", "42-8-38", "42-8-34", "42-8-60"),
    "post_conviction": ("5-5-40", "5-6-38", "9-14-42", "35-3-37", "42-8-60"),
    "eviction": ("44-7-50", "44-7-51", "44-7-52", "44-7-53", "44-7-54", "44-7-55", "44-7-56"),
    "custody": ("19-9-3", "19-9-1", "19-9-23"),
    "debt": ("9-3-24", "9-3-25", "9-11-12", "9-11-55", "9-11-60", "18-4-5"),
    "employment": ("34-7-1", "34-7-2"),
    "civil_suit": ("9-11-12", "9-11-55", "9-11-60"),
}


def plan_sections(plan: dict | None) -> list[str]:
    return list(SECTIONS.get((plan or {}).get("case_type") or "", ()))


def plan_hits(db, plan: dict | None, retrieval: dict, limit: int = 14) -> dict:
    """Put the case type's exact-citation sections first (verified-hit filter still applies)."""
    sections = plan_sections(plan)
    if not sections or db is None:
        return retrieval
    from .charge_check_service import lookup_sections
    try:
        with db.begin_nested():
            found = lookup_sections(db, sections)
    except Exception:  # never fail an answer because of this lookup
        return retrieval
    for h in found:
        h.pop("full_text", None)
        h["excerpt"] = (h.get("excerpt") or "")[:900]
    have = {str(h.get("citation") or "").lower() for h in found}
    rest = [h for h in retrieval.get("hits", []) if str(h.get("citation") or "").lower() not in have]
    return {**retrieval, "hits": (found + rest)[:limit]}


# ------------------------------------------------------------------ headings and prompt
CASE_AGAINST = "How they'd build the case against you"
FIGHT_BACK = "How to fight back"
CRIMINAL_HEADINGS = ("Quick answer", CASE_AGAINST, FIGHT_BACK, "Ways to challenge the evidence", "Your rights",
                     "Options to lessen the outcome", "Key deadlines", "Evidence to gather now",
                     "Questions to ask your lawyer", "Where to get help")
CIVIL_HEADINGS = ("Quick answer", CASE_AGAINST, FIGHT_BACK, "Ways to challenge their case", "Your rights",
                  "Motions and filings that could help", "Ways to resolve it", "Key deadlines", "Evidence to gather now",
                  "Questions to ask your lawyer", "Where to get help")
PAPERWORK_HEADING = "What helps in your paperwork"
ALL_HEADINGS = tuple(dict.fromkeys(CRIMINAL_HEADINGS + CIVIL_HEADINGS + (PAPERWORK_HEADING, "While you find that out")))
_KEYS = {h: re.sub(r"[^a-z]+", "_", h.lower()).strip("_") for h in ALL_HEADINGS}


def section_spec(plan: dict) -> tuple[tuple[str, str], ...]:
    heads = CRIMINAL_HEADINGS if plan.get("family") == "criminal" else CIVIL_HEADINGS
    extra = (PAPERWORK_HEADING,) if plan.get("source") == "document" else ()
    from .defense_help import MOTIONS_HEADING
    return tuple((_KEYS[h], h) for h in heads + extra) + ((re.sub(r"[^a-z]+", "_", MOTIONS_HEADING.lower()), MOTIONS_HEADING),)


_FOCUS = {
    "dui": "the stop's legal basis, field sobriety test administration, the implied consent warning and consent to the blood or breath test, "
           "how the blood sample was drawn, stored, and tested (chain of custody, lab, who drew it), observation period, and the separate "
           "driver's license (ALS) deadline",
    "drugs": "whether the stop and the car search were lawful (consent, probable cause, scope, K-9), who actually possessed the drugs "
             "(constructive possession, other passengers, whose car), lab testing and chain of custody, statements, and conditional discharge or First Offender",
    "theft": "intent (the State must prove intent to take), store video and loss-prevention reports, the value charged, how statements were taken, "
             "civil demand letters versus the criminal case, and First Offender, diversion, or pretrial intervention for a first offense "
             "(do not suggest a speedy-trial dismissal unless the user describes a long delay; Georgia shoplifting does not require leaving the store)",
    "traffic": "the officer's basis for the stop, how speed was measured (radar/laser calibration and training, pacing), errors on the citation, "
               "points and license consequences, and options like asking for reduced points, defensive driving, or a plea of nolo contendere "
               "(do not suggest First Offender, conditional discharge, or an accountability court for a traffic ticket)",
    "criminal": "what the State must prove for this charge, an unlawful stop, search, or arrest, identification, statements, witness credibility, "
                "and options like First Offender or pretrial diversion",
    "probation": "the exact condition said to be violated, notice of the violation, the right to a hearing and to a lawyer, the lower burden of "
                 "proof at a revocation hearing and challenging hearsay or unreliable evidence, graduated sanctions instead of jail, mitigation "
                 "(work, treatment, payments made), and how much of the sentence can be revoked",
    "post_conviction": "deadlines for a motion for new trial and appeal, errors at trial or in the plea (lawyer mistakes, an involuntary plea), "
                       "habeas corpus, sentence modification, First Offender retroactive relief, and record restriction",
    "eviction": "whether the landlord made a proper demand for possession, service of the summons, the deadline to answer, tender of rent as a "
                "defense, paying rent into court, repairs and retaliation, defects in the dispossessory affidavit, the right to a hearing, "
                "and the short appeal window",
    "custody": "the best interests of the child, a material change in circumstances for a modification, the child's own election at certain "
               "ages if a listed law says so, parenting plans, the other parent's conduct, and keeping records of parenting time and support",
    "debt": "whether the plaintiff owns the debt (standing and the chain of assignment), the statute of limitations, the exact amount and fees, "
            "answering before the deadline to avoid a default judgment, setting aside a default, and income protected from garnishment",
    "employment": "the type of employment (at-will or contract), unpaid wages and final pay, discrimination or retaliation, deadlines for agency "
                  "charges, and unemployment benefits",
    "civil_suit": "standing, proper service, answering on time, the statute of limitations, defenses and counterclaims, default judgments, "
                  "and settlement",
}


def prompt_block(plan: dict, app_motions: list[dict] | None = None) -> str:
    """Format instructions for a Defense Plan answer (replaces the general headings). ``app_motions``: the
    catalog motions already matched (verified) for these facts, named in "How to fight back"."""
    criminal = plan.get("family") == "criminal"
    heads = list(CRIMINAL_HEADINGS if criminal else CIVIL_HEADINGS)
    if plan.get("source") == "document":
        heads.insert(3, PAPERWORK_HEADING)
    paper = ("Under 'What helps in your paperwork' write 2-4 bullets on things in the paper that could help: missing or wrong "
             "information (names, dates, code sections, the court, the officer's or landlord's details), elements the paper does not "
             "allege, defects in notice or service, and dates or deadlines printed on it. Use only what the paper shows; if nothing stands out, say what to check. "
             if plan.get("source") == "document" else "")
    from .defense_help import MOTIONS_HEADING
    motions = (f"Do not write a '{MOTIONS_HEADING}' heading; the app adds the matching motions itself."
               if criminal else
               "Under 'Motions and filings that could help' name 1-3 filings that fit these facts (for example an answer, a motion to "
               "dismiss, a motion to set aside a default judgment, an appeal, or a petition to modify), one line each: what it does and how it helps.")
    lessen = ("Under 'Options to lessen the outcome' list only options that fit THIS charge: First Offender (not for traffic tickets), "
              "conditional discharge (only for drug possession), diversion or pretrial intervention, an accountability court (only if the "
              "user mentions addiction, substance use, mental health, or military service), record restriction, mitigation, and plea "
              "considerations (what to weigh before any plea)."
              if criminal else
              "Under 'Ways to resolve it' list options like a payment plan, settlement, mediation, or a consent order, only where they fit.")
    challenge = ("Under 'Ways to challenge the evidence' cover only the angles that fit: an illegal stop or search, identification, chain of custody "
                 "and testing, statements and Miranda, and " + ("the State's burden at a revocation hearing (lower than beyond a reasonable "
                 "doubt; never say 'beyond a reasonable doubt' for probation)" if plan.get("case_type") == "probation" else
                 "the State's burden to prove every element beyond a reasonable doubt") + "."
                 if criminal else
                 "Under 'Ways to challenge their case' cover only what fits: standing, proper notice and service, procedure, the statute of "
                 "limitations, the amount claimed, and the other side's burden of proof.")
    rights = ("Under 'Your rights' cover the rights that matter now: a lawyer or public defender, discovery, a speedy trial demand, and bond."
              if criminal else
              "Under 'Your rights' cover the rights that matter now: the deadline to answer, the right to a hearing, discovery, and appeal.")
    side = "the State (police and prosecutors)" if criminal else "the other side (for example the landlord, creditor, or other parent)"
    case_against = (f"Under \"{CASE_AGAINST}\" think like {side} using ONLY the user's facts: first bullet 'Likely "
                    f"{'charge' if criminal else 'claim'}: <name> (cite the listed Georgia law that defines it, if listed)'. Then one bullet per legal "
                    "element (2-4 elements), each as '<element name in 1-4 plain words, without the word Element>: They'd point to <what they likely already have from these facts, e.g. "
                    "bodycam, the search, statements, lab results, witnesses, the lease or ledger, ONLY where the user mentioned it>. They'd still need <what is missing>.' "
                    "For evidence the user did not mention, write it as what they would need or might have, in conditional terms ('They would need to show "
                    "you meant to keep it; if there is store video, they may use it'). Never say what a video, report, witness, or test shows unless the "
                    "user said so. Finish with one bullet 'Weak spots: <the gaps or weak points in their case>'.")
    fight_back = (f"Under \"{FIGHT_BACK}\" go element by element, matching the elements above: one bullet each as '<the same element name>: <one persuasive, "
                  f"motion-style sentence that starts like \"{'The State cannot establish possession because' if criminal else 'The landlord cannot show a proper demand for possession because'} ...\">. "
                  "Challenge: <the evidence challenge>. Motion: <the motion that attacks it>.' Write it the way a defense motion argues, built on "
                  "the user's facts and the listed laws. Use the exact motion names listed below when one fits. Later sections must not repeat "
                  "these points. "
                  "After 'Motion:' name a motion that attacks that element (for example to suppress, exclude, dismiss, or get discovery), never a "
                  "sentencing option like First Offender or conditional discharge. Only name a motion that fits this charge and these facts: no speedy-trial dismissal unless the user describes a long delay, no "
                  "accountability court unless they mention addiction, substance use, mental health, or military service. "
                  "Add one last bullet for any complete defense that fits (for example justification, entrapment, mistake of fact, tender of rent), "
                  "as '<Defense>: why it helps. Applies if ...'. At most 5 bullets.")
    if app_motions:
        fight_back += (" MOTIONS IN THE APP'S MOTION MAKER (name them exactly; do not cite a law for them unless it is listed above): " +
                       "; ".join(f"{m['title']} ({m['how_it_helps']})" for m in app_motions[:6]) + ".")
    return (f"AUTOMATIC DEFENSE PLAN ({plan.get('label')}): the user described their own situation. Build 'Your Defense Plan' for THESE "
            "facts. Be defense-first, strong and direct: you are on the user's side, so lead with what could help them most, without "
            "predicting or promising an outcome. NEVER invent facts: do not state anything the user did not say (no 'the video shows', 'the "
            "officer saw', 'you admitted'); phrase unknown evidence as what the other side would need or might have ('if there is video', "
            "'they may have'). Use these headings in this order, each on its "
            "own line exactly as written: " + "; ".join(heads) + ". Skip any heading (except Quick answer, Questions to ask your lawyer, and "
            "Where to get help) when nothing genuinely fits these facts; never pad. Under Quick answer write 2-3 short plain sentences (no bullets, "
            "no citations): first the strongest defense angle for these facts, then the most urgent next step. Never use the Quick answer to "
            "describe what the other side is allowed to do. " + case_against + " " + fight_back + " "
            f"{challenge} {rights} {motions} {lessen} {paper}"
            "Under 'Key deadlines' list only deadlines a listed law states or dates the user gave; otherwise one bullet saying to check the "
            "paperwork or the clerk right away. Under 'Evidence to gather now' list 3-4 concrete items for these facts. Under 'Questions to "
            "ask your lawyer' write 3-5 short questions ending with '?'. Under 'Where to get help' write one short line only; the app adds "
            "free legal help itself. Wherever you cite a listed law, add a plain clause on how it helps (e.g. 'O.C.G.A. § 17-5-30 lets you "
            "ask the judge to throw out illegally seized evidence'). Focus for this case type: " + _FOCUS.get(plan.get("case_type") or "", "") +
            ". Every bullet is one short line; at most 4 bullets under any heading; leave a blank line between headings. "
            "Never suggest lying, hiding assets, or destroying evidence.")


NOTICE = "This is legal information, not legal advice."


def with_notice(analysis: str) -> str:
    """Every plan ends with the not-legal-advice notice (as the footnote, merged with the Code-edition note)."""
    text = str(analysis or "").rstrip()
    if NOTICE in text:
        return text
    m = re.search(r"(?m)^Note:\s*", text)
    if m:
        return text[:m.start()] + "Note: " + NOTICE + " " + text[m.end():]
    return text + "\n\nNote: " + NOTICE


def max_words(plan: dict) -> int:
    return 760 if plan.get("source") == "document" else 700


def title_line(plan: dict) -> str:
    return f"{PLAN_TITLE}: {plan['label']}" if plan.get("label") else PLAN_TITLE


_DELAY = re.compile(r"speedy|delay|taking (so|too) long|been (?:\w+ )?(?:months|years?)|no trial date|waiting (?:on|for) (?:court|trial)|"
                    r"(?:months|years?) (?:and|with) no (?:trial|court)", re.I)
_TREATMENT = re.compile(r"addict|substance (?:use|abuse)|dependen|rehab|treatment|relaps|mental(?:ly)? (?:health|ill)|ptsd|bipolar|"
                        r"depress|schizo|veteran|military|served in the", re.I)


def _unfit(plan: dict) -> list[re.Pattern]:
    """Options/motions that don't fit this plan's charge and facts (dropped from motions and from bullet lines)."""
    facts = plan.get("facts") or ""
    kind = plan.get("case_type")
    bad = []
    if not _DELAY.search(facts):
        bad.append(re.compile(r"speedy[- ]trial (?:right )?dismiss|dismiss\w* (?:for|on) (?:a )?(?:violation of )?(?:the )?(?:constitutional )?speedy", re.I))
    if not _TREATMENT.search(facts):
        bad.append(re.compile(r"accountability court|drug court|mental health court|veterans? court", re.I))
    if kind == "traffic":
        bad.append(re.compile(r"first offender|conditional discharge", re.I))
    elif kind != "drugs":
        bad.append(re.compile(r"conditional discharge", re.I))
    return bad


def fit_motions(plan: dict, motions: list[dict]) -> list[dict]:
    """Drop catalog motions that don't fit the charge (e.g. speedy-trial dismissal without a delay, First Offender for a ticket)."""
    if not plan:
        return motions
    facts = plan.get("facts") or ""
    kind = plan.get("case_type")
    out = []
    for m in motions or []:
        k = m.get("key")
        if k == "speedy_trial_constitutional" and not _DELAY.search(facts):
            continue
        if k == "accountability_court" and not _TREATMENT.search(facts):
            continue
        if k == "conditional_discharge" and kind != "drugs":
            continue
        if k in ("first_offender", "retroactive_first_offender") and kind == "traffic":
            continue
        out.append(m)
    return out


_SENTENCING = re.compile(r"first offender|conditional discharge|accountability court|pretrial (?:diversion|intervention)", re.I)
_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
_CLAIMED = re.compile(r"\b(?:the |store |security |surveillance )?(video|footage|camera|body ?cam|dash ?cam)( clearly)? shows\b", re.I)


def scrub(plan: dict, analysis: str) -> str:
    """Server-side guard on the model's plan: drop bullets naming options that don't fit the charge, and turn an invented
    'the video shows' (when the user never mentioned video) into a conditional."""
    if not plan:
        return analysis
    bad = _unfit(plan)
    facts = plan.get("facts") or ""
    lines = []
    for line in str(analysis or "").split("\n"):
        head, sep, motion = line.partition(" Motion:")
        if sep and _SENTENCING.search(motion):
            line = head.rstrip()  # a sentencing option is not a motion that attacks an element
        if _BULLET.match(line) and any(b.search(line) for b in bad):
            head, sep, motion = line.partition(" Motion:")
            if sep and any(b.search(motion) for b in bad) and not any(b.search(head) for b in bad):
                line = head.rstrip()  # keep the argument, drop only the motion that doesn't fit
            else:
                continue
        lines.append(line)
    text = "\n".join(lines)
    if not re.search(r"video|footage|camera|\bcam\b|bodycam|dashcam|recorded", facts, re.I):
        text = _CLAIMED.sub(lambda m: f"any {m.group(1).lower()} would have to show", text)
    return text


def before_note(analysis: str, block: str) -> str:
    """Put ``block`` (e.g. the deadline check) before the 'Note:' footnote, not after it."""
    text = str(analysis or "").rstrip()
    m = re.search(r"(?m)^Note:", text)
    if not m:
        return text + "\n\n" + block
    return text[:m.start()].rstrip() + "\n\n" + block + "\n\n" + text[m.start():]


def motion_question(plan: dict) -> str:
    """Text used to pick catalog motions (criminal plans only)."""
    facts = plan.get("facts") or ""
    if plan.get("case_type") == "traffic":
        return facts + " misdemeanor charge"
    if plan.get("case_type") == "dui" and not re.search(r"\bdui\b", facts):
        return facts + " dui charge"
    return facts


def insert_before(analysis: str, section: str, anchors: tuple[str, ...]) -> str:
    if not section:
        return analysis
    text = str(analysis or "")
    for a in anchors:
        m = re.search(rf"(?im)^\s*{re.escape(a)}\s*:?\s*$", text)
        if m:
            return text[:m.start()].rstrip() + "\n\n" + section + "\n\n" + text[m.start():].lstrip()
    return None  # caller falls back


FOLLOW_UPS = {
    "dui": ("How do I request an ALS hearing with DDS?", "Can the blood test be challenged in Georgia?", "What happens at a first DUI court date?"),
    "drugs": ("How does a motion to suppress evidence work in Georgia?", "Who qualifies for conditional discharge in Georgia?", "What is constructive possession?"),
    "theft": ("Who qualifies for First Offender treatment in Georgia?", "Do I have to pay a store's civil demand letter?", "Can a shoplifting charge be restricted from my record?"),
    "traffic": ("How do points on a Georgia license work?", "Can I contest a traffic ticket in court?", "What happens if I miss my court date for a ticket?"),
    "criminal": ("How does a motion to suppress evidence work in Georgia?", "How do I demand a speedy trial in Georgia?", "Who qualifies for First Offender treatment in Georgia?"),
    "probation": ("What happens at a probation revocation hearing?", "Can I get a lawyer for a probation violation?", "How much of my probation can be revoked?"),
    "post_conviction": ("How do I file a notice of appeal in Georgia?", "What is a motion for new trial?", "Can my record be restricted in Georgia?"),
    "eviction": ("What happens at a dispossessory hearing?", "Can I pay rent into the court registry?", "How long do I have to appeal an eviction?"),
    "custody": ("How do I change a custody order?", "What counts as a material change in circumstances?", "What does the court consider for custody in Georgia?"),
    "debt": ("How long can a creditor sue over a debt in Georgia?", "How do I answer a debt lawsuit?", "What income is protected from garnishment?"),
    "employment": ("How do I get my final paycheck in Georgia?", "What is the deadline to file a discrimination charge?", "Can I get unemployment if I was fired?"),
    "civil_suit": ("How do I answer a lawsuit in Georgia?", "What happens if I miss the deadline to answer?", "Can I file a counterclaim?"),
}


def follow_ups(plan: dict) -> list[str]:
    if plan.get("status") == "clarify":
        return list(CLARIFY_EXAMPLES[plan.get("family") or "criminal"])
    return list(FOLLOW_UPS.get(plan.get("case_type") or "", ()))


def meta(plan: dict) -> dict:
    out = {"status": "built" if plan["status"] == "build" else "needs_details", "case_type": plan.get("case_type"),
           "label": plan.get("label") or "", "family": plan.get("family"), "title": title_line(plan)}
    if plan["status"] == "clarify":
        out["questions"] = list(plan["questions"])
    if plan.get("source"):
        out["source"] = plan["source"]
    return out


# ------------------------------------------------------------------ uploaded papers
def document_situation(result: dict, question: str = "") -> str:
    """The facts read from an uploaded paper, as the user's own situation for the plan."""
    lines = ["Build my defense plan from my court paperwork."]
    if result.get("document_type"):
        lines.append("Paper: " + result["document_type"])
    if result.get("charges_or_claims"):
        lines.append("Charges or claims on my paper: " + "; ".join(result["charges_or_claims"]))
    if result.get("key_dates"):
        lines.append("Dates on my paper: " + "; ".join(result["key_dates"]))
    if result.get("summary"):
        lines.append("What the paper says: " + result["summary"])
    if result.get("helpful_flags"):
        lines.append("Possible problems in the paper (from reading it): " + "; ".join(result["helpful_flags"]))
    if question.strip():
        lines.append("My question: " + question.strip())
    text = result.get("extracted_text") or ""
    if text:
        lines.append("Text read from my paper:\n" + text[:2500])
    return "\n".join(lines)[:3900]


def document_plan(result: dict) -> dict:
    """Plan decision for a paper: detect the case type from what the paper says."""
    blob = " ".join([result.get("document_type") or "", " ".join(result.get("charges_or_claims") or []),
                     result.get("summary") or "", (result.get("extracted_text") or "")[:3000]]).lower()
    kind = detect(blob)
    if kind:
        label, family = _TYPE[kind]
        return {"status": "build", "case_type": kind, "label": label, "family": family, "facts": blob[:1500], "source": "document"}
    family = "civil" if re.search(_VAGUE_CIVIL, blob) else "criminal"
    return {"status": "clarify", "case_type": None, "label": "", "family": family, "facts": blob[:1500],
            "questions": list(CLARIFY[family]), "source": "document"}
