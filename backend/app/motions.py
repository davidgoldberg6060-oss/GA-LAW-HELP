"""'Motions that could help' for each My Case stage, plus fill-in-the-blank motion templates.

Citations are Georgia Code sections checked against the stored law library at request time;
templates never cite case law and are clearly marked as drafts to review with a lawyer.
"""
from __future__ import annotations

import re
from datetime import date

GOALS = {"dismiss": "Could get the case dismissed or charges dropped/reduced",
         "sentence": "Could lower the sentence or time served",
         "other": "Could otherwise help"}
GOAL_ORDER = {"dismiss": 0, "sentence": 1, "other": 2}

TEMPLATE_BANNER = ("TEMPLATE – NOT LEGAL ADVICE. Review with a lawyer before filing. Fill in every [blank]. "
                   "Check the current law and local court rules. This draft cites only Georgia Code sections; add case law only after a lawyer checks it.")


def O(s):
    return f"O.C.G.A. § {s}"


def _has(text, *words):
    return any(re.search(r"\b" + re.escape(w) + r"\b", text) for w in words)


# Each motion: key, title, goal, what it does, cites, deadline, rule (date field, days), stages,
# fit(text, answers) -> (score 0-3, reason or None, question dict or None), relief (for the draft), facts prompt.
def _fit_suppress(t, a):
    ans = a.get("search_warrant")
    if ans == "no" or _has(t, "without a warrant", "no warrant", "warrantless", "without consent", "didn't consent", "did not consent", "no consent"):
        return 3, "The search may have been done without a warrant or consent.", None
    if ans == "yes":
        return 1, "A warrant was used; a lawyer can still check whether it was valid.", None
    if _has(t, "search", "searched", "found", "drugs", "weed", "gun", "car", "house", "pocket"):
        return 2, "Evidence was found in a search.", {"id": "search_warrant", "q": "Was the search done with a warrant?", "options": ["yes", "no", "not sure"]}
    return 0, None, {"id": "search_warrant", "q": "Was anything found in a search? Was it done with a warrant?", "options": ["yes", "no", "not sure"]}


def _fit_immunity(t, a):
    if _has(t, "self defense", "self-defense", "defending", "defend myself", "defended", "attacked me", "jumped me", "swung first"):
        return 3, "The facts describe self-defense.", None
    if _has(t, "fight", "battery", "assault", "shot", "stabbed", "hit"):
        return 1, "Force was used; immunity fits only if it was self-defense.", {"id": "self_defense", "q": "Was the force used to defend against an attack?", "options": ["yes", "no"]}
    return 0, None, None


def _fit_first_offender(t, a):
    if a.get("prior_felony") == "no" or _has(t, "no prior", "first offense", "first time", "no record", "never been in trouble"):
        return 3, "No prior felony was mentioned.", None
    if a.get("prior_felony") == "yes":
        return 0, None, None
    return 1, None, {"id": "prior_felony", "q": "Does the person have any prior felony conviction?", "options": ["yes", "no"]}


def _fit_conditional(t, a):
    if _has(t, "possession", "drugs", "weed", "marijuana", "cocaine", "pills", "controlled substance", "meth"):
        s = 3 if (a.get("prior_drug") == "no" or _has(t, "first offense", "no prior", "first time")) else 2
        return s, "It's a drug possession case.", None if s == 3 else {"id": "prior_drug", "q": "Any prior drug conviction?", "options": ["yes", "no"]}
    return 0, None, None


def _fit_time_credit(t, a):
    if _has(t, "jail", "locked up", "held", "custody", "days", "months", "before trial", "before sentencing", "time served"):
        return 2, "Time was spent in custody before sentencing.", None
    return 1, None, {"id": "jail_time", "q": "How many days was the person held before sentencing?", "options": []}


def _fit_concurrent(t, a):
    if _has(t, "counts", "consecutive", "two cases", "multiple charges", "back to back", "stacked"):
        return 2, "There are multiple counts or sentences.", None
    return 0, None, None


def _fit_lawyer(t, a):
    if _has(t, "lawyer", "attorney", "public defender", "counsel") and _has(t, "never", "didn't", "did not", "failed", "bad", "ineffective", "wouldn't"):
        return 3, "The facts describe problems with the lawyer.", None
    return 1, None, None


def _fit_no_appeal(t, a):
    if _has(t, "never filed", "no appeal", "didn't file", "did not file", "never appealed") and _has(t, "appeal"):
        return 3, "The lawyer may never have filed an appeal.", None
    return 1, None, None


def _fit_evidence(t, a):
    if _has(t, "new evidence", "new witness", "dna", "recanted", "lied", "found out"):
        return 3, "New evidence was mentioned.", None
    return 0, None, None


def _is_homicide(t):
    return _has(t, "murder", "felony murder", "killed", "shot and killed", "manslaughter", "died", "homicide", "body")


def _fit_lesser(t, a):
    if _is_homicide(t):
        return 3 if _has(t, "attacked", "self defense", "self-defense", "defending", "provoked", "heat of passion", "fight") else 2, \
            "A homicide charge can include lesser offenses like voluntary or involuntary manslaughter.", None
    return 0, None, None


def _fit_jury_charge(t, a):
    s, _, _ = _fit_immunity(t, a)
    return (3 if s >= 3 else 0), ("Self-defense is the main defense; the jury must be told about justification." if s >= 3 else None), None


def _fit_statements(t, a):
    if a.get("statement") == "yes" or _has(t, "confess", "statement", "interrogat", "questioned", "told police", "talked to police", "admitted"):
        return 3 if (a.get("statement_voluntary") == "no" or _has(t, "threat", "promised", "no lawyer", "without a lawyer", "miranda", "drunk", "high", "scared")) else 2, \
            "Statements were made to police.", None
    return 1, None, {"id": "statement", "q": "Did the person talk to police or give a statement?", "options": ["yes", "no"]}


def _fit_bond(t, a):
    if _is_homicide(t) or _has(t, "armed robbery", "rape", "kidnapping"):
        return 2, "For murder and other listed serious charges, only a superior court judge can set bond.", None
    return 2, None, None


def _always(score):
    return lambda t, a: (score, None, None)


MOTIONS = [
    dict(key="bond_reduction", title="Motion for bond (or to reduce bond)", goal="other", stages=["arrested", "pretrial"],
         what="Asks the judge to set or lower bond so the person can be released while the case is pending. For murder and other listed charges, only a superior court judge can grant bond.", cites=["17-6-1"],
         deadline="Can be filed any time while the person is held.", fit=_fit_bond,
         relief="set a reasonable bond, or reduce the bond already set, with any conditions the Court finds appropriate",
         facts="[Explain ties to the community: job, family, home, no flight risk, no danger to others.]"),
    dict(key="suppress", title="Motion to suppress evidence", goal="dismiss", stages=["pretrial", "trial"],
         what="Asks the judge to throw out evidence from an illegal search or seizure. Without that evidence, charges are often dropped.",
         cites=["17-5-30", "17-5-21"], deadline="Usually within 10 days after arraignment, unless the judge allows more time.",
         rule=("arraignment_date", 10), fit=_fit_suppress,
         relief="suppress all evidence obtained as a result of the search and seizure described below and return any lawfully possessed property",
         facts="[Date, place, who searched, what was searched, whether there was a warrant or consent, what was found.]"),
    dict(key="immunity", title="Motion for self-defense immunity", goal="dismiss", stages=["pretrial", "trial"],
         what="Asks for a pretrial hearing to declare the person immune from prosecution for force used in self-defense. If granted, the case ends.",
         cites=["16-3-24.2", "16-3-20", "16-3-21", "16-3-23", "16-3-23.1"], deadline="Before trial.", fit=_fit_immunity,
         relief="hold a pretrial hearing and declare the Defendant immune from criminal prosecution for the use of force described below",
         facts="[What the other person did, why the Defendant believed force was necessary, injuries, witnesses, video.]"),
    dict(key="suppress_statements", title="Motion to suppress statements", goal="dismiss", stages=["pretrial", "trial"],
         what="Asks the judge to exclude statements to police that weren't voluntary (for example, made after threats or promises).",
         cites=["24-8-824"], deadline="With pretrial motions (10 days after arraignment), unless the judge allows more time.",
         rule=("arraignment_date", 10), fit=_fit_statements,
         relief="hold a hearing on the voluntariness of any statements attributed to the Defendant and exclude any statement not shown to be voluntary",
         facts="[When and where the statement was made, who was present, whether rights were explained, any threats, promises, intoxication or requests for a lawyer.]"),
    dict(key="lesser_offenses", title="Request jury instructions on lesser offenses", goal="sentence", stages=["pretrial", "trial"],
         what="Asks that the jury be allowed to consider lesser crimes (e.g. voluntary or involuntary manslaughter instead of murder), which carry much lower sentences.",
         cites=["16-1-6", "16-5-2", "16-5-3", "16-5-1"], deadline="Written requests before the jury is charged; objections before the jury deliberates.",
         fit=_fit_lesser, relief="instruct the jury on the lesser included offenses identified below",
         facts="[Facts supporting each lesser offense: provocation, sudden passion, lack of intent.]"),
    dict(key="jury_charge_justification", title="Request jury charge on justification (self-defense)", goal="dismiss", stages=["trial"],
         what="Asks the judge to tell the jury that justified self-defense is a complete defense, including no duty to retreat.",
         cites=["16-3-20", "16-3-21", "16-3-23.1", "17-8-58"], deadline="Before the jury is charged; object before it deliberates.",
         fit=_fit_jury_charge, relief="charge the jury on justification, use of force in defense of self or others, and no duty to retreat",
         facts="[Evidence at trial that supports self-defense.]"),
    dict(key="demurrer", title="Demurrer / motion to dismiss the charge", goal="dismiss", stages=["pretrial"],
         what="Challenges the indictment or accusation itself (for example, missing elements or wrong dates).",
         cites=["17-7-110", "17-7-111", "17-7-113"], deadline="Within 10 days after arraignment, unless extended.",
         rule=("arraignment_date", 10), fit=_always(1),
         relief="dismiss the indictment/accusation (or the counts identified below) for the defects stated",
         facts="[Identify each count and the defect: missing element, vague date or place, wrong statute.]"),
    dict(key="speedy_trial", title="Demand for speedy trial", goal="dismiss", stages=["pretrial"],
         what="Forces the State to try the case quickly. If it isn't tried that term or the next (with juries available), the law requires acquittal. Capital cases have their own rule.",
         cites=["17-7-170", "17-7-171"], deadline="At the court term of the indictment/accusation or the next regular term.", fit=_always(2),
         relief="",
         facts=""),
    dict(key="conditional_discharge", title="Conditional discharge (first drug possession)", goal="dismiss", stages=["pretrial", "plea"],
         what="For a first drug-possession case, the court can defer proceedings and dismiss after probation is completed, with no conviction.",
         cites=["16-13-2"], deadline="Ask before sentencing.", fit=_fit_conditional,
         relief="defer further proceedings and place the Defendant on probation under conditional discharge",
         facts="[Confirm no prior drug convictions; describe treatment, work, school.]"),
    dict(key="first_offender", title="First Offender treatment", goal="dismiss", stages=["plea", "sentenced"],
         what="If there's no prior felony, the judge can defer a judgment of guilt; completing the sentence means no conviction.",
         cites=["42-8-60"], deadline="Ask before sentencing.", fit=_fit_first_offender,
         relief="sentence the Defendant under the First Offender Act without an adjudication of guilt",
         facts="[No prior felony; work, family, school and community support.]"),
    dict(key="time_credit", title="Motion for jail-time credit", goal="sentence", stages=["sentenced", "prison"],
         what="Makes sure every day spent in jail before sentencing is credited toward the sentence.",
         cites=["17-10-11"], deadline="Ask at sentencing or as soon as an error is found.", fit=_fit_time_credit,
         relief="order that the Defendant receive full credit for all days spent in confinement as stated below",
         facts="[List each period in custody: dates in and out, facility.]"),
    dict(key="concurrent", title="Request for concurrent sentences", goal="sentence", stages=["plea", "sentenced"],
         what="Asks that sentences on multiple counts or cases be served at the same time instead of back to back.",
         cites=["17-10-10"], deadline="At sentencing, or within the sentence-modification window.", fit=_fit_concurrent,
         relief="order that the sentences identified below be served concurrently",
         facts="[List each case/count and its sentence.]"),
    dict(key="sentence_mod", title="Motion to modify or reduce sentence", goal="sentence", stages=["sentenced", "prison", "probation"],
         what="The sentencing judge can correct, reduce, suspend or probate the sentence if the motion is filed in time.",
         cites=["17-10-1"], deadline="Within 1 year after sentencing, or 120 days after the appeal is decided (whichever is later).",
         rule=("sentence_date", 365), fit=_always(2),
         relief="reduce, suspend or probate all or part of the sentence imposed",
         facts="[Programs completed, good conduct, work, family needs, health, remorse, support waiting at home.]"),
    dict(key="new_trial", title="Motion for new trial", goal="dismiss", stages=["sentenced"],
         what="Asks the trial judge for a new trial because of errors at trial, an ineffective lawyer, or new evidence.",
         cites=["5-5-40", "5-5-23"], deadline="Within 30 days after the judgment is entered.", rule=("sentence_date", 30), fit=_fit_lawyer,
         relief="set aside the verdict and judgment and grant a new trial",
         facts="[Each error: what happened, when, and why it mattered.]"),
    dict(key="appeal", title="Notice of appeal", goal="dismiss", stages=["sentenced", "appeal"],
         what="Starts an appeal to a higher court.", cites=["5-6-38"],
         deadline="Within 30 days after judgment, or after the ruling on a motion for new trial.", rule=("sentence_date", 30), fit=_always(2),
         relief="", facts=""),
    dict(key="habeas", title="Petition for writ of habeas corpus", goal="dismiss", stages=["appeal", "prison"],
         what="Challenges the conviction or sentence for constitutional violations, such as a lawyer who failed to file an appeal or investigate.",
         cites=["9-14-42", "9-14-43", "9-14-44"], deadline="Within 4 years for a felony (1 year for a misdemeanor) from when the conviction became final.",
         rule=("final_date", 4 * 365), fit=lambda t, a: max(_fit_lawyer(t, a), _fit_no_appeal(t, a)),
         relief="issue the writ of habeas corpus, vacate the conviction and sentence, and grant any other relief that is just",
         facts="[Each constitutional violation: what the lawyer did or failed to do (e.g. never filed the requested appeal), and how it harmed the case.]"),
    dict(key="extraordinary_mnt", title="Extraordinary motion for new trial (new evidence / DNA)", goal="dismiss", stages=["prison"],
         what="For important evidence found after trial, including requests for DNA testing.", cites=["5-5-41"], deadline=None, fit=_fit_evidence,
         relief="grant a new trial (and/or order DNA testing) based on the newly discovered evidence described below",
         facts="[The new evidence, when and how it was found, why it couldn't be found before trial, and how it would change the result.]"),
    dict(key="parole", title="Parole / clemency application support", goal="sentence", stages=["prison"],
         what="The State Board of Pardons and Paroles decides parole and other relief. Support letters and program records help.",
         cites=["42-9-42", "42-9-43"], deadline=None, fit=_always(1), relief="", facts=""),
]
BY_KEY = {m["key"]: m for m in MOTIONS}


def motions_for(stage: str, text: str, answers: dict, lookup, deadline_fn) -> tuple[list, list]:
    out, questions, seen_q = [], [], set()
    for m in MOTIONS:
        if stage not in m["stages"]:
            continue
        cites = [c for c in (lookup(O(s)) for s in m["cites"]) if c]
        if not cites:
            continue
        score, reason, q = m["fit"](text, answers)
        if q and q["id"] not in answers and q["id"] not in seen_q:
            seen_q.add(q["id"]); questions.append(q)
        out.append({"key": m["key"], "title": m["title"], "goal": m["goal"], "goal_label": GOALS[m["goal"]], "what": m["what"],
                    "fits": reason, "score": score, "deadline": m["deadline"], "deadline_status": deadline_fn(m.get("rule")),
                    "citations": cites, "draftable": bool(m["relief"])})
    out.sort(key=lambda x: (-x["score"] if x["score"] >= 3 else 0, GOAL_ORDER[x["goal"]], -x["score"]))
    return out, questions


def draft(key: str, details: dict, lookup) -> dict:
    m = BY_KEY.get(key)
    if not m or not m["relief"]:
        raise ValueError("No template is available for that filing.")
    cites = [c for c in (lookup(O(s)) for s in m["cites"]) if c]
    if not cites:
        raise ValueError("The law for this motion isn't in GA.LAW.HELP yet.")
    county = (details.get("county") or "").strip() or "[COUNTY]"
    court = "SUPERIOR" if "superior" not in (details.get("court") or "").lower() and not details.get("court") else (details.get("court") or "SUPERIOR").upper().replace(" COURT", "")
    name = (details.get("defendant") or "").strip() or "[DEFENDANT'S FULL NAME]"
    case_no = (details.get("case_number") or "").strip() or "[CASE NUMBER]"
    charge = (details.get("charge") or "").strip() or "[CHARGE(S)]"
    situation = (details.get("situation") or "").strip()
    law_lines = "\n".join(f"   • {c['citation']} ({c['title']})" for c in cites)
    title = m["title"].upper().replace("PETITION FOR", "PETITION FOR").replace("/", "OR")
    caption = (f"IN THE {court} COURT OF {county.upper()} COUNTY\nSTATE OF GEORGIA\n\n"
               f"STATE OF GEORGIA,\n        v.                                   Case No. {case_no}\n{name},\n        Defendant.\n")
    if key == "habeas":
        caption = (f"IN THE SUPERIOR COURT OF [COUNTY WHERE HELD] COUNTY\nSTATE OF GEORGIA\n\n"
                   f"{name}, Petitioner,\n        v.                                   Civil Action No. [LEAVE BLANK FOR CLERK]\n[WARDEN'S NAME], Warden, Respondent.\n")
    party = "Petitioner" if key == "habeas" else "Defendant"
    body = (f"{title}\n\n"
            f"COMES NOW {name}, {party}, [pro se / by and through counsel], and respectfully moves this Court to {m['relief']}. "
            f"In support, {party} shows the following:\n\n"
            f"1. {party} is charged with / was convicted of: {charge}.\n\n"
            f"2. Facts: {situation or ''}\n   {m['facts']}\n\n"
            f"3. Georgia law: this motion is made under the following Code section(s):\n{law_lines}\n\n"
            f"4. [Explain how the law applies to these facts. Do not add case law unless a lawyer has checked it.]\n\n"
            f"WHEREFORE, {party} respectfully asks that this Court {m['relief']}, and grant any other relief that is just.\n")
    today = date.today().strftime("%B %d, %Y")
    sig = (f"\nRespectfully submitted this [DAY] day of [MONTH], [YEAR].\n\n______________________________\n{name}\n"
           f"[Address / inmate number and facility]\n[Phone / email]\n[If represented: attorney name, Georgia Bar No., address]\n\n"
           f"CERTIFICATE OF SERVICE\nI certify that I served a copy of this filing on the [District Attorney / Attorney General] by [mail/e-filing/hand delivery] "
           f"at [address] on [date].\n\n______________________________\n{name}\n")
    text = f"{TEMPLATE_BANNER}\n\n{caption}\n{body}{sig}\n(Draft generated {today} by GA.LAW.HELP. Template only.)\n"
    return {"key": key, "title": m["title"], "text": text, "citations": cites, "banner": TEMPLATE_BANNER}
