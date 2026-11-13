"""'Things you may not know to ask': short, tappable follow-ups that surface related problems, the root of the
problem, and hidden deadlines or side issues, picked from the facts the user gave (max 4, each with a one-line why).

Deterministic on purpose: no model call, no citations, and every 'why' line is a plain, conservative statement."""
from __future__ import annotations

import re

HEADING = "Things you may not know to ask"
MAX_ITEMS = 4
MAX_CHIPS = 3  # the 1.7.4 apps show up to 3 tappable follow-up chips

# (question the user can tap to ask, why it matters, only-when regex or None, skip-when regex or None)
Item = tuple[str, str, str | None, str | None]

_ARREST = r"arrest|charged|charge|jail|booked|locked up|picked up|cited|warrant|police|officer|cops?"

ITEMS: dict[str, tuple[Item, ...]] = {
    "dui": (
        ("Do I have to appeal my license suspension within 30 days?",
         "The ALS license appeal is separate from the criminal case; miss the 30 days and the suspension can start automatically.",
         None, r"\bals\b|license hearing|appealed (the|my) (license|suspension)"),
        ("Can the blood or breath test, or my refusal, be used against me?",
         "Whether the implied consent warning was read correctly can decide if the result or a refusal comes in.", None, None),
        ("Does a crash or injury make a DUI charge worse?",
         "A crash or injury can raise the charge and add insurance and civil claims.", r"crash|accident|wreck|hit (a|an|the|someone)|injur", None),
        ("Will a DUI affect my CDL or a job where I drive?",
         "Commercial drivers face stricter license rules, so it changes what to fight for first.",
         r"\bcdl\b|truck|drive for (work|a living)|uber|lyft|delivery|commercial", None),
    ),
    "drugs": (
        ("Can they prove the drugs were mine if others were there?",
         "If others had access to the car or home, the State must prove you knew about and controlled the drugs.",
         r"car|passenger|friend|roommate|house|apartment|others?|someone", None),
        ("Will a drug charge affect my job, housing, or a professional license?",
         "Side effects can last longer than the sentence, so ask before any plea.", None, None),
    ),
    "theft": (
        ("Do I have to pay the store's civil demand letter?",
         "That letter is separate from the criminal case; paying it does not make the charge go away.", None, r"civil demand"),
        ("Can a shoplifting charge be kept off a record?",
         "First Offender, diversion, or record restriction may protect jobs and school; ask before any plea.", None, None),
        ("Does the value of the items change the charge?",
         "The dollar amount can decide misdemeanor versus felony, so the price they claim matters.", None, None),
    ),
    "traffic": (
        ("Will this ticket put points on my license or suspend it?",
         "Georgia suspends a license at 15 points in 24 months, and sooner for drivers under 21.", None, None),
        ("Is this a super speeder ticket with a separate state fee?",
         "Going 85+ anywhere or 75+ on a two-lane road adds a state fee; left unpaid, it can suspend your license.",
         r"speed|mph|super speeder|too fast", None),
        ("What happens if I miss the court date on the ticket?",
         "Missing it can lead to a license suspension and a bench warrant.", None, None),
        ("Does this ticket affect my CDL or insurance?",
         "Commercial drivers have stricter rules, and points can raise insurance for years.", None, None),
    ),
    "probation": (
        ("Is there a probation warrant or hold out for me?",
         "A warrant can mean arrest before the hearing; ask about bond on the violation.", None, r"warrant|hold"),
        ("Can they revoke me because I couldn't afford the fines?",
         "The court should look at whether you tried to pay; not being able to pay is different from refusing.",
         r"fine|fee|pay|money|afford", None),
        ("Are these only technical violations, and does that limit jail time?",
         "Georgia treats technical violations differently from a new charge, which can limit the jail time.", None, r"new charge|arrested again"),
        ("What proof of my work or attempts to comply should I bring?",
         "Pay stubs, schedules, and messages to your officer can show the violation wasn't willful.", r"work|job|shift|told", None),
    ),
    "post_conviction": (
        ("Is it too late to file a motion for new trial or an appeal?",
         "Those deadlines are short, often 30 days from sentencing.", None, None),
        ("Could I get First Offender treatment after the fact?",
         "If no one told you about First Offender, retroactive relief may be possible.", None, None),
        ("Can my record be restricted after this?", "Restriction can keep the case off most job background checks.", None, None),
    ),
    "eviction": (
        ("How many days do I have to answer the eviction?",
         "You have 7 days after being served to answer, or the landlord can win by default.", None, r"answered|filed (an|my) answer"),
        ("Did my landlord give proper notice and a demand before filing?",
         "A missing demand for possession or improper service can get the case dismissed.", None, None),
        ("Is this eviction retaliation for a complaint I made?",
         "Georgia bars some evictions that retaliate for good-faith repair or code complaints.",
         r"complain|code enforcement|report|repair|mold|leak|broken|roach|heat|\bac\b|condition", None),
        ("Do problems with the home's condition affect what I owe?",
         "Repair problems you reported may support a defense or reduce what you owe.", None, None),
        ("What happens to my security deposit?",
         "The landlord must return it or give an itemized list of damages after you move out.", None, None),
    ),
    "custody": (
        ("Do threats or violence matter for custody or a protective order?",
         "Family violence weighs heavily on custody and can support a protective order.",
         None, None),
        ("Should child support change along with custody?",
         "Support doesn't change on its own; it usually needs its own order.", None, r"child support"),
        ("What if the other parent moves out of state with the child?",
         "A move can be a material change that supports changing custody.", r"mov|relocat|out of state", None),
        ("What records of parenting time should I keep?",
         "Logs, messages, and missed visits are often the strongest evidence.", None, None),
    ),
    "debt": (
        ("How long do I have to answer the lawsuit?",
         "Missing the answer deadline can lead to a default judgment and garnishment.", r"sued|lawsuit|served|court|summons", None),
        ("Is this debt too old to sue on?",
         "Old debts may be past the statute of limitations, which can end the case.", None, None),
        ("Do they have proof they own the debt?",
         "A debt buyer must show the chain of ownership from the original lender.", None, None),
        ("Can they garnish my wages or benefits?",
         "Some income, like Social Security, is protected from garnishment.", None, None),
    ),
    "employment": (
        ("Should I apply for unemployment now?", "Apply right away; waiting can cost weeks of benefits.",
         r"fired|terminated|laid off|let go", r"unemployment"),
        ("Was this retaliation for a complaint, leave, or injury?",
         "Retaliation and discrimination claims have strict agency deadlines, often 180 days.", None, None),
        ("Am I owed a final paycheck or unpaid overtime?",
         "Unpaid wages and overtime can be claimed even after you leave.", None, None),
        ("Should I sign a severance agreement or release?",
         "Signing a release can give up claims you didn't know you had.", None, None),
    ),
    "civil_suit": (
        ("How long do I have to answer the lawsuit?",
         "Missing the answer deadline can lead to a default judgment.", None, r"answered|filed (an|my) answer"),
        ("Will my insurance defend me?",
         "Your insurer may have to defend you; tell them right away.", r"accident|wreck|car|injur|damage|crash", None),
        ("Was I properly served?", "Improper service can be a defense.", None, None),
        ("Can I file a counterclaim?",
         "Some claims you have against them must be raised now or they can be lost.", None, None),
    ),
}

# Every criminal arrest (not tickets, probation, or after a conviction): bond, holds, immigration, search, statements.
ARREST: tuple[Item, ...] = (
    ("Does it matter if police searched me, my car, or my phone?",
     "If there was a search, an illegal one can get the evidence thrown out.", None, r"search|searched|found"),
    ("Can what I told police be used against me?",
     "Statements taken without proper warnings, or under pressure, can sometimes be challenged.", None, None),
    ("What happens if I break a bond condition?",
     "Breaking a bond condition, like no contact or a curfew, can send you back to jail before trial.", r"bond|bail|released|jail|booked", None),
    ("Can this arrest cause a probation hold?",
     "If you're already on probation, a new arrest can trigger a hold and a separate revocation.", r"probation|parole", None),
    ("Could a plea affect immigration status for a non-citizen?",
     "For non-citizens, even First Offender or a minor plea can count for immigration; get advice before any plea.", None, None),
)
_ARREST_TYPES = {"dui", "drugs", "theft", "criminal"}


def _ok(item: Item, facts: str) -> bool:
    _q, _why, when, unless = item
    if when and not re.search(when, facts, re.I):
        return False
    return not (unless and re.search(unless, facts, re.I))


def pick(case_type: str | None, facts: str, n: int = MAX_ITEMS) -> list[dict]:
    """Up to ``n`` {question, why} items that fit these facts: fact-matched items first, then the defaults."""
    facts = str(facts or "")
    own = [i for i in ITEMS.get(case_type or "", ()) if _ok(i, facts)]
    extra = [i for i in ARREST if _ok(i, facts)] if case_type in _ARREST_TYPES else []
    if case_type in _ARREST_TYPES and not own and not re.search(_ARREST, facts, re.I):
        extra = extra[:2]
    matched = [i for i in own if i[2]] + [i for i in extra if i[2]]
    rest = [i for i in own if not i[2]]
    rest_extra = [i for i in extra if not i[2]]
    # Mix: the case's own hidden issues lead, with up to 2 arrest-wide ones (search, statements, immigration).
    order = matched + rest[:2] + rest_extra[:2] + rest[2:] + rest_extra[2:]
    out, seen = [], set()
    for q, why, _w, _u in order:
        if q not in seen:
            seen.add(q)
            out.append({"question": q, "why": why})
    return out[:n]


def section(items: list[dict]) -> str:
    """Plan section text. Each bullet splits into a tappable question (head) and its 'Why it matters' line (detail)."""
    if not items:
        return ""
    return HEADING + "\n" + "\n".join(f"• {i['question']} Why it matters: {i['why']}" for i in items)


def chips(items: list[dict]) -> list[str]:
    return [i["question"] for i in items if len(i["question"]) <= 120][:MAX_CHIPS]
