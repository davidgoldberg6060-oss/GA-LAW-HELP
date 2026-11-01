"""'My Case' guide: next steps, motions and filings for each stage of a Georgia criminal case.

Every citation is checked against the stored law library at request time and dropped if it is
not there (never invented). Deadline text paraphrases the cited section; users can open the full
text inline. This is general legal information, not legal advice.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta

DISCLAIMER = ("This is general legal information, not legal advice. Deadlines can depend on details of your case. "
              "Contact a lawyer or the Georgia Public Defender Council as soon as possible.")

RESOURCES = [
    {"title": "Georgia Public Defender Council", "url": "https://www.gapubdef.org/"},
    {"title": "Georgia Innocence Project", "url": "https://www.georgiainnocenceproject.org/"},
    {"title": "Southern Center for Human Rights", "url": "https://www.schr.org/"},
    {"title": "State Board of Pardons and Paroles", "url": "https://pap.georgia.gov/"},
    {"title": "Georgia Legal Aid", "url": "https://www.georgialegalaid.org/"},
    {"title": "State Bar of Georgia: find a lawyer", "url": "https://www.gabar.org/public/find-a-lawyer"},
]

STAGES = [
    ("arrested", "Arrested / bond"),
    ("pretrial", "Charged / pretrial"),
    ("plea", "Plea offer"),
    ("trial", "Trial"),
    ("sentenced", "Sentenced"),
    ("appeal", "Appeal"),
    ("prison", "In prison: get out or reduce time"),
    ("probation", "Probation / parole"),
    ("record", "Clear my record"),
]
STAGE_LABELS = dict(STAGES)

def O(sec: str) -> str:
    return f"O.C.G.A. § {sec}"

# key, title, explanation, citations, deadline (plain text or None), deadline rule, where to file, issue tags
def _opt(key, title, what, cites, deadline=None, where=None, rule=None, tags=()):
    return {"key": key, "title": title, "what": what, "cites": [O(c) for c in cites], "deadline": deadline,
            "where": where, "rule": rule, "tags": list(tags)}

OPTIONS: dict[str, list[dict]] = {
    "arrested": [
        _opt("first_appearance", "First appearance in front of a judge",
             "After an arrest on a warrant, police must bring you before a judge who can set bond.",
             ["17-4-26"], "Within 72 hours after an arrest on a warrant.", "The magistrate court in the county of arrest.",
             rule=("arrest_date", 3)),
        _opt("bond", "Ask for bond", "Ask the judge to set a bond you can afford, or lower one already set. Some serious charges can only get bond from a superior court judge.",
             ["17-6-1"], None, "Magistrate court, or superior court for the charges listed in the law."),
        _opt("grand_jury_90", "If you are held without bond: 90-day grand jury rule",
             "If bond is refused, you are entitled to have a grand jury hear the charge within 90 days of being locked up. If not, ask for bond.",
             ["17-7-50"], "Within 90 days after the date you were jailed (if bond was refused).", "Superior court where the case is pending.",
             rule=("arrest_date", 90)),
    ],
    "pretrial": [
        _opt("pretrial_motions", "File pretrial motions on time",
             "Demurrers (challenges to how the charge is written), special pleas and other pretrial motions must be filed on time and in writing.",
             ["17-7-110", "17-7-111"], "Within 10 days after arraignment, unless the judge gives more time.", "The court where you were arraigned.",
             rule=("arraignment_date", 10)),
        _opt("speedy_trial", "Demand a speedy trial",
             "A written demand filed with the clerk and served on the prosecutor and judge. If you are not tried that term or the next (with juries available), the law requires discharge and acquittal.",
             ["17-7-170", "17-7-171"], "File at the court term when you are indicted or accused, or the next regular term.", "Clerk of the court where the charge is filed."),
        _opt("suppress", "Motion to suppress evidence", "Ask the judge to throw out evidence from an illegal search or seizure.",
             ["17-5-30"], "Usually with pretrial motions (10 days after arraignment), unless extended.", "Trial court.", tags=("search",)),
        _opt("discovery", "Get the evidence against you (discovery)",
             "The prosecutor must share statements, reports and evidence before trial.", ["17-16-1", "17-16-4"],
             "The prosecutor must disclose no later than 10 days before trial or when the court orders.", "Trial court."),
        _opt("immunity", "Self-defense immunity hearing",
             "If you used force in self-defense, ask for a pretrial hearing to be declared immune from prosecution.",
             ["16-3-24.2", "16-3-21"], None, "Trial court, before trial.", tags=("self_defense",)),
    ],
    "plea": [
        _opt("plea_choices", "Understand your plea choices",
             "You can plead not guilty, guilty, or (with the judge's approval, in non-capital cases) nolo contendere. Each has different consequences.",
             ["17-7-93", "17-7-95"], None, "Trial court."),
        _opt("first_offender", "Ask about First Offender treatment",
             "If you have no prior felony conviction, the judge can defer a judgment of guilt. Finishing your sentence can mean no conviction.",
             ["42-8-60"], "Ask before you are sentenced.", "Trial court, as part of the plea."),
        _opt("plea_vs_trial", "Plea vs. trial: what to weigh",
             "A plea gives up a trial and most appeal rights; a trial risks a longer sentence if convicted. Ask your lawyer about the sentence range and any mandatory minimums.",
             ["17-10-1", "17-10-6.1", "17-10-7"], None, None),
    ],
    "trial": [
        _opt("discovery_trial", "Make sure you have all the evidence", "Ask your lawyer to confirm discovery is complete before trial.",
             ["17-16-4"], "The prosecutor must disclose no later than 10 days before trial.", "Trial court."),
        _opt("suppress_trial", "Challenge illegal evidence", "If not already done, ask about a motion to suppress.", ["17-5-30"], None, "Trial court."),
        _opt("immunity_trial", "Self-defense", "Justification is a defense; ask about an immunity motion before trial.", ["16-3-21", "16-3-24.2", "16-3-20"], None, "Trial court.", tags=("self_defense",)),
    ],
    "sentenced": [
        _opt("mnt", "Motion for new trial", "Ask the trial judge for a new trial because of legal errors, ineffective lawyer, or new evidence.",
             ["5-5-40", "5-5-23"], "Within 30 days after the judgment is entered.", "The trial court that convicted you.",
             rule=("sentence_date", 30)),
        _opt("notice_of_appeal", "Notice of appeal", "Start an appeal to a higher court.", ["5-6-38"],
             "Within 30 days after the judgment, or 30 days after the ruling on a motion for new trial.", "Filed with the trial court clerk.",
             rule=("sentence_date", 30)),
        _opt("sentence_mod", "Ask to reduce or modify the sentence",
             "The sentencing judge can correct, reduce, suspend or probate the sentence if you file in time.", ["17-10-1"],
             "Within 1 year after the sentence is imposed, or 120 days after the appeal is decided (whichever is later).", "The sentencing court.",
             rule=("sentence_date", 365)),
    ],
    "appeal": [
        _opt("notice_of_appeal", "Notice of appeal", "File in time or the right to a direct appeal can be lost.", ["5-6-38", "5-6-34"],
             "Within 30 days after the judgment, or after the ruling on a motion for new trial.", "Trial court clerk.", rule=("sentence_date", 30)),
        _opt("out_of_time", "Missed the appeal deadline?",
             "Talk to a lawyer right away. Georgia's appellate courts have limited out-of-time appeals in trial courts; habeas corpus (below) is often the route now.",
             ["9-14-42"], None, None),
    ],
    "prison": [
        _opt("sentence_mod", "Sentence reduction or modification", "The sentencing judge can reduce or suspend part of the sentence if you file in time.",
             ["17-10-1"], "Within 1 year after sentencing, or 120 days after the appeal is decided (whichever is later).", "The sentencing court.",
             rule=("sentence_date", 365), tags=("sentence",)),
        _opt("illegal_sentence", "Void or illegal sentence",
             "A sentence the law does not allow (for example above the maximum) can be challenged. Ask a lawyer to review it.",
             ["17-10-1"], "Ask a lawyer; void sentences can generally be raised at any time.", "The sentencing court.", tags=("sentence",)),
        _opt("habeas", "Habeas corpus (including bad lawyer / ineffective assistance)",
             "Challenge the conviction or sentence for violations of your constitutional rights, such as an ineffective lawyer.",
             ["9-14-40", "9-14-41", "9-14-42", "9-14-43", "9-14-44", "9-14-48", "9-14-52"],
             "Within 4 years for a felony (1 year for a misdemeanor) from when the conviction became final.",
             "Superior court of the county where you are held.", rule=("final_date", 4 * 365), tags=("lawyer",)),
        _opt("extraordinary_mnt", "New evidence: extraordinary motion for new trial",
             "If important evidence was found after trial that could change the result.", ["5-5-41", "5-5-23"],
             None, "The trial court that convicted you.", tags=("evidence",)),
        _opt("dna", "DNA testing", "A person convicted of a felony can ask the trial court to order DNA testing of evidence.",
             ["5-5-41"], None, "The trial court that convicted you.", tags=("evidence", "dna")),
        _opt("first_offender_retro", "First Offender, retroactively",
             "If you qualified for First Offender but were never told, you can (with the prosecutor's consent) petition for exoneration and discharge.",
             ["42-8-66"], None, "The court where you were convicted.", tags=("first_offender",)),
        _opt("parole", "Parole, clemency or commutation",
             "The State Board of Pardons and Paroles decides parole and other relief from sentence. Family can send letters of support.",
             ["42-9-42", "42-9-43", "42-9-20"], None, "State Board of Pardons and Paroles (pap.georgia.gov)."),
        _opt("conditions", "Conditions inside (medical, food, safety)",
             "Put medical requests in writing (sick-call) and keep copies; file grievances; have family contact the facility.",
             ["42-5-2", "42-4-4"], None, "The facility, then the Georgia Department of Corrections."),
    ],
    "probation": [
        _opt("revocation", "Probation violation / revocation hearing",
             "You have the right to a hearing before probation is revoked. Bring proof that you complied.", ["42-8-34.1", "42-8-38"],
             None, "The court that sentenced you."),
        _opt("early_term", "Ask to end probation early or change conditions", "Ask the sentencing court to modify the sentence or conditions.",
             ["17-10-1", "42-8-34.1"], None, "The sentencing court."),
        _opt("parole_prob", "Parole questions", "Parole is supervised by the State Board of Pardons and Paroles.", ["42-9-42"], None, "State Board of Pardons and Paroles."),
    ],
    "record": [
        _opt("restriction", "Record restriction (Georgia's version of expungement)",
             "Ask to have arrests or charges that did not end in conviction, and some convictions, restricted from public view.",
             ["35-3-37"], None, "The prosecutor's office or the court, depending on the case.", tags=("record",)),
        _opt("first_offender_done", "Finished First Offender?", "Completing First Offender means no conviction; check the record was updated.",
             ["42-8-60", "42-8-62"], None, "Clerk of the sentencing court."),
        _opt("pardon", "Pardon", "A pardon from the State Board of Pardons and Paroles can restore rights.", ["42-9-42"], None, "State Board of Pardons and Paroles."),
    ],
}

NEXT_STEPS = {
    "arrested": ["The person arrested should not talk about the case (jail calls are recorded) and should ask for a lawyer.", "Find out the booking number, charges and the first appearance date from the jail or sheriff's website.", "Ask for a public defender at the first appearance if a lawyer isn't affordable."],
    "pretrial": ["Get a copy of the charging papers (indictment or accusation) and the arraignment date.", "Ask the lawyer which pretrial motions will be filed before the 10-day deadline.", "Jail calls and messages are recorded; don't discuss the case on them."],
    "plea": ["Ask exactly what sentence the offer means and whether it's First Offender.", "Ask what a plea means for the defendant's record, license, job or immigration status.", "The defendant doesn't have to decide on the spot and can ask for time to talk to the lawyer."],
    "trial": ["Ask the lawyer whether family can testify or help find witnesses and evidence.", "If the defendant is in custody, arrange court clothes.", "Don't talk to jurors or witnesses."],
    "sentenced": ["Deadlines are short: 30 days for a new-trial motion or appeal.", "Get a copy of the sentence and the case number.", "Tell the lawyer in writing if the defendant wants to appeal."],
    "appeal": ["Ask the appellate lawyer for the record and transcript.", "Keep copies of everything filed.", "Send the appellate lawyer any issues to raise."],
    "prison": ["Get a copy of the sentence, the plea or trial record, and the case number.", "Check the 1-year sentence-modification and the habeas deadlines below.", "Contact a lawyer, the Georgia Innocence Project, or the Southern Center for Human Rights."],
    "probation": ["Keep proof of every payment, class and check-in.", "If there's a warrant, talk to a lawyer about turning in safely.", "Ask for the conditions in writing."],
    "record": ["Get the criminal history from the GBI or local police (the person may need to request it themselves).", "Note which charges were dismissed, dead-docketed or completed First Offender.", "Contact the prosecutor's office about record restriction."],
}

FAMILY_TIPS = {
    "arrested": ["Family can usually post bond through the jail, a bonding company, or with property. Ask the jail which options it accepts.", "Put money on the person's books (commissary/phone account) through the jail's approved service.", "Call the public defender's office for the county to give them your contact information."],
    "pretrial": ["Contact the public defender or lawyer with information or witnesses that could help.", "Keep the lawyer's number and every court date in one place.", "Visit or set up calls through the jail's approved system."],
    "plea": ["You can share with the lawyer anything that supports a lighter sentence (job offer, family duties, treatment plans)."],
    "trial": ["Attend court if you can; a supportive family in the courtroom can matter."],
    "sentenced": ["Write a respectful support letter for the judge (job, housing and family support waiting after release).", "Put money on the person's books and set up calls or visits once a facility is assigned to a facility."],
    "appeal": ["Keep in touch with the appellate lawyer and send them any new information."],
    "prison": ["Write support letters to the State Board of Pardons and Paroles about housing, work and family support.", "Put money on books and set up visits or calls through the Georgia Department of Corrections.", "If there's a medical or safety emergency, call the facility and the GDC ombudsman."],
    "probation": ["Help with rides to check-ins, classes and court."],
    "record": [],
}


def _third_person(t: str) -> str:
    for a, b in ((r"\byour\b", "the defendant's"), (r"\bYour\b", "The defendant's"), (r"\byou\b", "the defendant"), (r"\bYou\b", "The defendant")):
        t = re.sub(a, b, t)
    for a, b in (("the defendant are", "the defendant is"), ("the defendant have", "the defendant has"), ("The defendant have", "The defendant has"), ("the defendant file", "the defendant files"),
                 ("but were never", "but was never"), ("the defendant can (with", "they can (with"), ("Finishing the defendant's sentence", "Finishing the sentence"),
                 ("If the defendant are held", "If the defendant is held"), ("Make sure the defendant has all", "Make sure the defense has all"),
                 ("Bring proof that the defendant complied", "Bring proof of compliance"), ("Understand the defendant's plea choices", "Understand the plea choices")):
        t = t.replace(a, b)
    return t


_DETECT = [
    ("prison", r"(?i)\b(in prison|i'?m locked up|doing time|serving (a |my )?(sentence|time)|get (me )?out|reduce my (time|sentence)|habeas|parole board|commutation)"),
    ("record", r"(?i)\b(expunge|record restriction|clear my record|seal my record)"),
    ("probation", r"(?i)\b(probation|parole|\bpo\b|violated)"),
    ("appeal", r"(?i)\b(appeal|appellate|out of time)"),
    ("sentenced", r"(?i)\b(sentenced|got sentenced|new trial|sentence (modification|reduction))"),
    ("plea", r"(?i)\b(plea (deal|offer|bargain)|take a plea|plead guilty|first offender)"),
    ("trial", r"(?i)\b(trial date|going to trial|jury trial)"),
    ("pretrial", r"(?i)\b(indicted|arraign|charged with|speedy trial|suppress|discovery|court date)"),
    ("arrested", r"(?i)\b(arrested|locked me up|bond|bail|booked|warrant)"),
]


def detect_stage(text: str) -> str | None:
    for stage, pat in _DETECT:
        if re.search(pat, text or ""):
            return stage
    return None


_ISSUE_WORDS = {"lawyer": ("lawyer", "attorney", "counsel"), "evidence": ("evidence", "witness", "dna"), "dna": ("dna",),
                "sentence": ("sentence", "illegal", "too long"), "self_defense": ("self defense", "self-defense", "defend"),
                "search": ("search", "stop"), "first_offender": ("first offender",), "record": ("record",)}


def _parse_date(v) -> date | None:
    if not v:
        return None
    try:
        return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _deadline(rule, dates: dict, today: date) -> dict | None:
    if not rule:
        return None
    field, days = rule
    start = dates.get(field) or (dates.get("sentence_date") if field == "final_date" else None)
    if start is None:
        return None
    due = start + timedelta(days=days)
    left = (due - today).days
    approx = field == "final_date" and not dates.get("final_date")
    return {"due": due.isoformat(), "days_left": left, "passed": left < 0, "approximate": approx,
            "label": ("Likely passed" if left < 0 else f"{left} days left") + (" (estimate)" if approx else "")}


def build_guide(db, *, stage: str, details: dict | None = None, today: date | None = None, exists=None) -> dict:
    from .models import LegalAuthority
    from .answer_format import short_title
    if stage not in OPTIONS:
        raise ValueError("Choose a stage of your case.")
    details = details or {}
    today = today or date.today()
    dates = {k: _parse_date(details.get(k)) for k in ("arrest_date", "arraignment_date", "sentence_date", "final_date")}
    issues = " ".join(str(details.get(k, "")) for k in ("issues", "situation", "charge")).lower()
    cache: dict[str, dict | None] = {}

    def lookup(c: str):
        if c not in cache:
            row = exists(c) if exists else db.query(LegalAuthority).filter(LegalAuthority.citation == c).first()
            cache[c] = None if row is None else {"citation": c, "title": short_title(getattr(row, "title", "") or "", c), "id": getattr(row, "id", None)}
        return cache[c]

    options, timeline = [], []
    for o in OPTIONS[stage]:
        cites = [x for x in (lookup(c) for c in o["cites"]) if x]
        if not cites:
            continue  # never show an option without a real stored law behind it
        dl = _deadline(o["rule"], dates, today)
        relevant = any(w in issues for t in o["tags"] for w in _ISSUE_WORDS.get(t, ()))
        item = {"key": o["key"], "title": o["title"], "what": o["what"], "deadline": o["deadline"], "where": o["where"],
                "deadline_status": dl, "highlight": relevant, "citations": cites}
        options.append(item)
        if dl:
            timeline.append({"title": o["title"], **dl})
    options.sort(key=lambda x: (not x["highlight"], x["deadline_status"]["passed"] if x["deadline_status"] else False))
    timeline.sort(key=lambda t: t["due"])
    laws, seen = [], set()
    for o in options:
        for c in o["citations"]:
            if c["citation"] not in seen:
                seen.add(c["citation"]); laws.append(c)
    for o in options:  # neutral wording: works whether the case is the user's or someone else's
        o["what"] = _third_person(o["what"]); o["title"] = _third_person(o["title"])
    return {"stage": stage, "stage_label": STAGE_LABELS[stage],
            "next_steps": NEXT_STEPS[stage], "family_tips": FAMILY_TIPS[stage],
            "options": options,
            "timeline": timeline, "laws_cited": laws, "resources": RESOURCES, "disclaimer": DISCLAIMER,
            "stages": [{"key": k, "label": v} for k, v in STAGES]}
