"""Curated "Where to get help" routing.

Resources come only from this catalogue (checked against each provider's own page on VERIFIED_ON),
never from the model. Routing uses only the user's current question, and a county only if the user
named one. No acceptance is promised; eligibility is decided by each provider.
"""
from __future__ import annotations
import re

VERIFIED_ON = "2026-11-07"
METRO_COUNTIES = ("clayton", "cobb", "dekalb", "fulton", "gwinnett")

R = {
    "public_defender": {
        "name": "Public defender (Georgia Public Defender Council)", "cost": "Free if the court finds you qualify",
        "what": "Lawyers for people charged with a crime who can't afford one. Offices are assigned by the county where the alleged offense happened. Not for civil cases.",
        "next": "Ask at your first court appearance or contact the public defender office for that county.",
        "url": "https://georgiacourts.gov/find-your-public-defender/", "phone": None,
        "source": "https://georgiacourts.gov/find-your-public-defender/"},
    "gpdc_contact": {
        "name": "Georgia Public Defender Council — find your office", "cost": "Free to call",
        "what": "Helps you reach the circuit public defender office. Start with the office or a supervisor if you have a problem with appointed counsel.",
        "next": "Call (800) 676-4432 or use Find Your Public Defender.",
        "url": "https://georgiacourts.gov/find-your-public-defender/", "phone": "800-676-4432",
        "source": "https://georgia.gov/contacts/public-defender-council-contact"},
    "bar_cap": {
        "name": "State Bar of Georgia — Client Assistance Program", "cost": "Free",
        "what": "Can try informal help if you are having trouble reaching your lawyer. It does not take over your case or remove the lawyer.",
        "next": "Call (404) 527-8759.",
        "url": "https://www.gabar.org/programs/client-assistance-program", "phone": "404-527-8759",
        "source": "https://www.gabar.org/programs/client-assistance-program"},
    "bar_grievance": {
        "name": "State Bar of Georgia — file a grievance", "cost": "Free to file",
        "what": "A written ethics complaint with the Office of the General Counsel. A grievance does not remove the lawyer from your case or stop court dates.",
        "next": "Read the Bar's instructions and file on the Bar's website. The lawyer is likely to see what you submit.",
        "url": "https://www.gabar.org/general-counsel/file-a-grievance", "phone": None,
        "source": "https://www.gabar.org/general-counsel/file-a-grievance"},
    "lawyer_directory": {
        "name": "State Bar of Georgia — Find a Lawyer directory", "cost": "Private lawyers (usually paid)",
        "what": "Search for lawyers by practice area. The State Bar does not refer clients itself.",
        "next": "Search the directory, then contact lawyers directly to ask about fees.",
        "url": "https://www.gabar.org/public/find-a-lawyer", "phone": None,
        "source": "https://www.gabar.org/public/find-a-lawyer"},
    "atlanta_legal_aid": {
        "name": "Atlanta Legal Aid Society", "cost": "Free for people who qualify (income and other rules)",
        "what": "Free civil legal help (not criminal) mainly for Clayton, Cobb, DeKalb, Fulton and Gwinnett counties.",
        "next": "Apply online or call the office for your county; have any papers you received ready.",
        "url": "https://atlantalegalaid.org/get-help-2/", "phone": "404-524-5811",
        "source": "https://atlantalegalaid.org/get-help-2/"},
    "glsp": {
        "name": "Georgia Legal Services Program (GLSP)", "cost": "Free for people who qualify (generally low income, or 60+)",
        "what": "Free civil legal help (not criminal) in the 154 Georgia counties outside Clayton, Cobb, DeKalb, Fulton and Gwinnett.",
        "next": "Apply online or by phone to find out if you qualify.",
        "url": "https://www.glsp.org/need-help/", "phone": "1-833-457-7529",
        "source": "https://www.glsp.org/need-help/"},
    "senior_legal_aid": {
        "name": "Georgia Senior Legal Aid", "cost": "Free", "what": "Civil legal help for Georgia residents age 60 or older, statewide.",
        "next": "Call to ask about your issue.", "url": "https://atlantalegalaid.org/get-help-2/", "phone": "404-389-9992",
        "source": "https://atlantalegalaid.org/get-help-2/"},
    "georgialegalaid": {
        "name": "GeorgiaLegalAid.org", "cost": "Free information",
        "what": "Plain-language guides, court forms and FAQs from Georgia's legal aid programs.",
        "next": "Look up your topic and any forms you may need.",
        "url": "https://www.georgialegalaid.org/", "phone": None, "source": "https://www.georgialegalaid.org/contact-us"},
    "court_self_help": {
        "name": "Georgia Courts self-help resources", "cost": "Free information",
        "what": "Court procedure guides, forms and self-help centers. Court staff can explain procedure but cannot give legal advice.",
        "next": "Find the self-help program or law library for your court.",
        "url": "https://georgiacourts.gov/a2j/self-help-resources/", "phone": None,
        "source": "https://georgiacourts.gov/a2j/self-help-resources/"},
    "dds_als": {
        "name": "Georgia DDS — Administrative License Suspension hearing requests", "cost": "Agency (filing fee applies)",
        "what": "How to request an ALS hearing or pay fees after a DUI arrest. The deadline is on your notice; act quickly.",
        "next": "Read your DDS notice and follow the DDS instructions for submitting a hearing request.",
        "url": "https://dds.georgia.gov/georgia-licenseid/violations-suspensions-revocations/alsoptions", "phone": None,
        "source": "https://dds.georgia.gov/georgia-licenseid/violations-suspensions-revocations/alsoptions"},
    "consumer_protection": {
        "name": "Georgia Attorney General — Consumer Protection Division", "cost": "Free to file a complaint",
        "what": "Takes complaints about unfair or deceptive business practices. It does not act as your lawyer.",
        "next": "File a complaint online with receipts, contracts and messages.",
        "url": "https://consumer.georgia.gov/", "phone": "1-800-869-1123", "source": "https://consumer.georgia.gov/"},
    "dv_hotline": {
        "name": "Georgia 24-Hour Domestic Violence Hotline", "cost": "Free, 24/7",
        "what": "Connects you to the nearest certified domestic violence shelter and advocates. In immediate danger, call 911.",
        "next": "Call any time.", "url": "https://gcadv.org/get-help/call-24-hour-statewide-hotline/", "phone": "1-800-334-2836",
        "source": "https://gcadv.org/get-help/call-24-hour-statewide-hotline/"},
    "gdc_family": {
        "name": "Georgia Department of Corrections — friends and family questions", "cost": "Agency",
        "what": "Where to ask about someone in state prison custody, including conditions and the Ombudsman.",
        "next": "Use the GDC family page; keep notes of every call.",
        "url": "https://gdc.georgia.gov/friends-and-family/questions-about-your-loved-ones", "phone": None,
        "source": "https://gdc.georgia.gov/friends-and-family/questions-about-your-loved-ones"},
}

CRIMINAL = r"\b(arrest|charged?|charges|crime|criminal|self[- ]defen[cs]e|immunity hearing|stand your ground|assault|battery|theft|shoplift|robbery|burglary|drugs?|marijuana|possession|warrant|bond|bail|probation|indict|plea|misdemeanor|felony|dui|under the influence|murder|manslaughter|appeal (?:a|my|the|his|her) conviction|convict)"
CIVIL = r"\b(evict|dispossessory|landlord|tenant|lease|rent|deposit|debt|collector|garnish|divorce|custody|visitation|child support|alimony|benefits|snap|medicaid|unemployment|wages?|fired|employer|consumer|scam|refund|small claims|sue|lawsuit|foreclos|will|probate|estate|name change)"
DUI = r"\b(dui|under the influence|implied consent|license suspen|als hearing)"
CONSUMER = r"\b(scam|consumer|refund|deceptive|car dealer|lemon|warranty)"
DV = r"\b(domestic violence|abus(e|ive)|protective order|tpo|stalk|threaten(ed|ing) me|hit me|beat(s|ing)? me)"
SENIOR = r"\b(i'?m|i am|age|aged) (6\d|7\d|8\d|9\d)\b|\bsenior\b|\bover 60\b"
EXISTING_LAWYER = r"\b(my|our|his|her|their) (lawyer|attorney|public defender)\b"
_COUNTY = re.compile(r"\b([a-z][a-z\-]+(?: [a-z]+)?) county\b")


def named_county(question: str) -> str | None:
    m = _COUNTY.search((question or "").lower())
    return m.group(1).split()[-1] if m else None


def route(question: str) -> list[dict]:
    """Resources for the user's current question. [] when nothing specific matches."""
    from .civil_topics import PRISON, current_question
    q = current_question(question).lower()
    keys: list[str] = []
    from .defense_help import is_broad_defense
    criminal = bool(re.search(CRIMINAL, q)) or is_broad_defense(q)
    civil = bool(re.search(CIVIL, q))
    if re.search(DV, q):
        keys.append("dv_hotline")
    if re.search(DUI, q):
        keys.append("dds_als")
    from .public_defender_problems import detect as pd_detect
    if pd_detect(q):
        keys += ["gpdc_contact", "bar_cap", "bar_grievance", "lawyer_directory"]
    if criminal:
        if not pd_detect(q):
            keys += ["public_defender", "lawyer_directory"]
        else:
            keys += ["public_defender"]
    if re.search(PRISON, q):
        keys.append("gdc_family")
    if civil or re.search(DV, q):
        county = named_county(q)
        if county in METRO_COUNTIES:
            keys.append("atlanta_legal_aid")
        elif county:
            keys.append("glsp")
        else:
            keys += ["atlanta_legal_aid", "glsp"]
        if re.search(SENIOR, q):
            keys.append("senior_legal_aid")
        if re.search(CONSUMER, q):
            keys.append("consumer_protection")
        keys += ["georgialegalaid", "court_self_help"]
        if not criminal:
            keys.append("lawyer_directory")
    out, seen = [], set()
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append({"id": k, **R[k], "verified_on": VERIFIED_ON})
    return out


def section_text(question: str, resources: list[dict]) -> str:
    """Plain-text 'Where to get help' section built only from the catalogue."""
    from .civil_topics import current_question
    q = current_question(question).lower()
    lines = ["Where to get help"]
    if re.search(EXISTING_LAWYER, q):
        from .public_defender_problems import detect as pd_detect
        if pd_detect(q):
            lines.append("• If the problem is with your public defender or appointed lawyer, use the steps in \"Problem with my public defender?\" A State Bar grievance does not automatically remove them from your case.")
        else:
            lines.append("• If you already have a lawyer for this, ask them first; they know your case and deadlines.")
    if not resources:
        lines.append("• We don't have a specific verified resource for this question. GeorgiaLegalAid.org (free legal information) or the State Bar of Georgia Find a Lawyer directory (private lawyers) are general starting points.")
        return "\n".join(lines)
    county_note = len({r["id"] for r in resources} & {"atlanta_legal_aid", "glsp"}) == 2
    for r in resources:
        phone = f" Call {r['phone']}." if r.get("phone") else ""
        lines.append(f"• {r['name']} — {r['cost']}. {r['what']}{phone}")
    if county_note:
        lines.append("• Which legal aid office serves you depends on your county.")
    lines.append("• Providers decide eligibility; contacting them doesn't guarantee they can take your case.")
    return "\n".join(lines)


_HELP_HEAD = re.compile(r"(?im)^\s*(?:\d+[.)]\s*)?where to get help\s*:?\s*$")


def replace_help_section(analysis: str, question: str) -> tuple[str, list[dict]]:
    """Drop any model-written 'Where to get help' section and put the curated one in its place."""
    from .answer_format import _KNOWN_HEADINGS
    text = str(analysis or "")
    resources = route(question)
    m = _HELP_HEAD.search(text)
    tail = ""
    if m:
        rest = text[m.end():]
        stop = len(rest)
        for line in re.finditer(r"(?m)^.*$", rest):
            s = line.group(0).strip()
            if (s.lower().rstrip(":") in _KNOWN_HEADINGS and s.lower().rstrip(":") != "where to get help") or s.startswith("Note:"):
                stop = line.start()
                break
        tail = rest[stop:]
        text = text[:m.start()].rstrip()
    else:
        note = re.search(r"\n\s*Note:", text)
        if note:
            tail, text = text[note.start():], text[:note.start()].rstrip()
    new = text + "\n\n" + section_text(question, resources)
    if tail.strip():
        new += "\n\n" + tail.strip()
    return new, resources


# Fallback "Questions to ask your lawyer" when the model skipped or mis-filled the section.
# Questions only: no rules, deadlines, or assumptions about custody, family, or already having a lawyer.
LAWYER_QUESTIONS = (
    (r"self[- ]defen[cs]e|immunity|stand your ground|justification", ("Could self-defense or a pretrial immunity hearing apply to these facts?", "What evidence would help, and how should it be preserved?", "What are the risks, timing, and deadlines we should discuss?", "What would representation cost, or do I qualify for a public defender?")),
    (r"\bdui\b|under the influence|implied consent|license suspen", ("What happens with my license, and what deadline is on my notice?", "Should I request an administrative hearing or consider a permit option?", "How could the evidence in my case be challenged?", "What are the possible outcomes and costs?")),
    (r"\bappeal|new trial|convict", ("Is there still time to appeal or file a motion for new trial, and what is the exact deadline?", "What issues could be raised?", "Who handles the appeal, and what will it cost?")),
    (r"evict|dispossessory|landlord|tenant|lease|deposit", ("What defenses or options do I have in this situation?", "What deadline is on the papers I received, and how do I respond?", "What documents should I bring?", "What could happen at a hearing?")),
    (r"custody|visitation|divorce|child support|alimony|parenting", ("What factors will matter most in my situation?", "What documents and records should I gather?", "What is the process and timeline in my county?", "What will it cost, and are there free or reduced-fee options?")),
    (r"debt|collector|garnish|lawsuit|sued|small claims", ("Is this claim valid, and what defenses might apply?", "What deadline is on the papers I received?", "What income or property might be protected?", "What are my options to settle or respond?")),
    (r"record restrict|expung|criminal record|first offender", ("Is my record eligible for restriction, and how do I request it?", "What records should I get first?", "How long does the process take, and what does it cost?")),
    (r"arrest|charged?|warrant|bond|bail|probation|theft|shoplift|drug|assault|battery", ("What defenses could fit this charge, and what would the State have to prove?", "Could any stop, search, or statement be challenged with a motion?", "What evidence matters, and how should it be preserved?", "What are the next court dates and deadlines?", "What would representation cost, or do I qualify for a public defender?")),
    (r"injur|accident|wreck|negligen", ("Do I have a claim, and how long do I have to file?", "What evidence and records should I keep?", "How are fees usually handled for this kind of case?")),
)
_Q_HEAD = re.compile(r"(?im)^\s*questions to ask your lawyer\s*:?\s*$")
_STEPS_HEAD = re.compile(r"(?im)^\s*steps you can take\s*:?\s*$")


def lawyer_questions(question: str) -> list[str]:
    from .civil_topics import current_question
    q = current_question(question).lower()
    from .defense_help import is_broad_defense, BROAD_LAWYER_QUESTIONS
    if is_broad_defense(q):
        return list(BROAD_LAWYER_QUESTIONS)
    for pattern, items in LAWYER_QUESTIONS:
        if re.search(pattern, q):
            return list(items)
    return ["How does the law apply to my specific facts?", "What options do I have, and what are the risks of each?", "Are there deadlines I need to know about?", "What will this cost?"]


def _section_bounds(text: str, head: re.Match) -> int:
    from .answer_format import _KNOWN_HEADINGS
    rest = text[head.end():]
    for line in re.finditer(r"(?m)^.*$", rest):
        s = line.group(0).strip()
        if s.lower().rstrip(":") in _KNOWN_HEADINGS or s.startswith("Note:"):
            return head.end() + line.start()
    return len(text)


def ensure_lawyer_questions(analysis: str, question: str) -> str:
    """General answers carry 'Questions to ask your lawyer' (questions only) instead of 'Steps you can take'."""
    text = str(analysis or "")
    block = "Questions to ask your lawyer\n" + "\n".join("• " + q for q in lawyer_questions(question)) + "\n\n"
    m = _Q_HEAD.search(text)
    if m:
        end = _section_bounds(text, m)
        body = text[m.end():end]
        if "?" in body:
            steps = _STEPS_HEAD.search(text)
            if steps:
                text = text[:steps.start()] + text[_section_bounds(text, steps):]
            return text
        return text[:m.start()].rstrip() + "\n\n" + block + text[end:].lstrip()
    steps = _STEPS_HEAD.search(text)
    if steps:
        end = _section_bounds(text, steps)
        return text[:steps.start()].rstrip() + "\n\n" + block + text[end:].lstrip()
    help_head = _HELP_HEAD.search(text)
    if help_head:
        return text[:help_head.start()] + block + text[help_head.start():]
    return text.rstrip() + "\n\n" + block.rstrip()
