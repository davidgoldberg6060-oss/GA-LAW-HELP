"""Topic -> O.C.G.A. sections for general/civil questions.

Sections are looked up by EXACT citation (fast, indexed). Anything not in the database or not
verified is dropped later by the normal verified-hit filter, so this list can never add an
unverified authority to an answer.
"""
from __future__ import annotations
import logging
import re

_log = logging.getLogger(__name__)

PRISON = (r"(i'?m|i am|currently|been|still|son is|husband is|brother is|loved one is) (in|locked up in|stuck in) (prison|jail|the county|a cell)|incarcerat|\binmates?\b|\bmy cell\b|cell ?block|"
          r"correctional officers?|\bco'?s\b|\bguards?\b|solitary|the hole|commissary|grievance|department of corrections|state pen|penitentiary|"
          r"(prison|jail).{0,60}(no water|no food|no bed|no mattress|medical|cold|sick|conditions|mold)")
# Topics that must not fire when the person is talking about jail/prison conditions.
_NOT_IN_PRISON = ("evict", "contract", "neighbor", "wage")

TOPICS: tuple[tuple[str, tuple[str, ...]], ...] = (
    # Jail / prison conditions (sections confirmed present in the DB 2026-11-01).
    (PRISON, ("42-4-4", "42-4-32", "42-5-2", "42-5-58", "42-5-52", "42-4-31")),
    # Criminal / everyday questions (matched on the question plus slang-derived plain terms).
    (r"self defense|justification|use of force|stand your ground", ("16-3-21", "16-3-24.2", "16-3-23.1", "16-3-20")),
    (r"fight|battery|assault|affray", ("16-5-20", "16-5-21", "16-5-23", "16-5-23.1", "16-5-24", "16-11-32")),
    (r"shoplift", ("16-8-14", "16-8-2")),
    (r"robbery", ("16-8-40", "16-8-41", "16-8-2")),
    (r"controlled substance|marijuana|drugs?\b|cocaine|meth", ("16-13-30", "16-13-2")),
    (r"probation", ("42-8-38", "42-8-34.1")),
    (r"bail|bond", ("17-6-1",)),
    (r"warrant", ("17-4-40", "17-4-20")),
    (r"\barrest", ("17-4-20", "17-6-1")),
    (r"under the influence|\bdui\b", ("40-6-391", "40-5-67.1", "40-6-392")),
    (r"firearm|weapon", ("16-11-126", "16-11-127", "16-11-129")),
    (r"traffic citation|speeding", ("40-6-181", "40-13-1")),
    (r"repossession", ("11-9-609",)),
    (r"expung|record restrict|seal(ed|ing)? (my )?record|clear my record|criminal record", ("35-3-37", "42-8-62", "17-10-21")),
    (r"first offender", ("42-8-60", "42-8-62")),
    (r"security deposit|deposit back", ("44-7-30", "44-7-33", "44-7-34", "44-7-35")),
    (r"evict|dispossessory|landlord|tenant|lease|rent\b|notice to quit|repairs?", ("44-7-50", "44-7-51", "44-7-53", "44-7-55", "44-7-7", "44-7-13", "44-7-14")),
    (r"divorce|alimony|separat", ("19-5-1", "19-5-3", "19-5-5", "19-6-1")),
    (r"custody|visitation|parenting", ("19-9-1", "19-9-3")),
    (r"child support", ("19-6-15",)),
    (r"small claims|magistrate|sue (someone|him|her|them|my)|file a (law)?suit", ("15-10-2", "15-10-43", "15-10-41")),
    (r"garnish|wage(s)? (taken|withheld)|levy", ("18-4-1", "18-4-5", "18-4-20")),
    (r"debt|collector|collection|credit card|owe", ("9-3-24", "9-3-25", "18-4-5")),
    (r"contract|agreement|breach|warranty", ("13-1-1", "13-6-11", "9-3-24", "9-3-25")),
    (r"injur|accident|slip|negligen|wreck|dog bit", ("9-3-33", "51-1-6", "51-12-4", "9-3-31")),
    (r"wage|paycheck|fired|employ|overtime|final pay", ("34-7-1", "34-7-2", "34-4-3")),
    (r"scam|consumer|refund|deceptive|car dealer|lemon", ("10-1-393", "10-1-399")),
    (r"neighbor|trespass|nuisance|fence|property line|tree", ("41-1-1", "41-1-4", "51-9-1")),
    (r"name change|change my name", ("19-12-1",)),
    (r"\bwill\b|probate|estate|inherit|died without", ("53-4-20", "53-2-1", "15-9-30")),
)


def topic_sections(text: str, limit: int = 12) -> list[str]:
    low = (text or "").lower()
    out: list[str] = []
    in_prison = bool(re.search(PRISON, low))
    for pattern, sections in TOPICS:
        if in_prison and any(k in pattern for k in _NOT_IN_PRISON):
            continue
        if re.search(pattern, low):
            out.extend(s for s in sections if s not in out)
    return out[:limit]


def topic_hits(db, query: str, retrieval: dict, limit: int = 12) -> dict:
    """Put exact-citation topic hits first in ``retrieval['hits']`` (deduplicated)."""
    sections = topic_sections(query)
    if not sections or db is None:
        return retrieval
    from .charge_check_service import lookup_sections
    try:
        with db.begin_nested():
            hits = lookup_sections(db, sections)
    except Exception as exc:  # never fail an answer because of the topic lookup
        _log.warning("Topic citation lookup skipped: %s", type(exc).__name__)
        return retrieval
    for h in hits:
        h.pop("full_text", None)
        h["excerpt"] = (h.get("excerpt") or "")[:1200]
    have = {str(h.get("citation") or "").lower() for h in hits}
    rest = [h for h in retrieval.get("hits", []) if str(h.get("citation") or "").lower() not in have]
    return {**retrieval, "hits": (hits + rest)[:limit]}


FOLLOW_UPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (PRISON, ("How do I file a grievance in a Georgia prison or jail?", "How can my family report conditions to the Georgia Department of Corrections?", "Can I get free legal help while incarcerated?")),
    (r"expung|record restrict|criminal record", ("Which charges can be restricted in Georgia?", "How do I request record restriction from the prosecutor?", "Does First Offender status help my record?")),
    (r"security deposit|deposit back", ("How long does my landlord have to return my deposit?", "Can I sue for my deposit in small claims court?", "What can a landlord deduct from a deposit?")),
    (r"evict|dispossessory|landlord|tenant", ("How much notice does a Georgia landlord have to give?", "What happens at a dispossessory hearing?", "Can my landlord lock me out?")),
    (r"divorce|custody|child support|alimony", ("How is child support calculated in Georgia?", "How long does an uncontested divorce take?", "What does the court consider for custody?")),
    (r"debt|garnish|collector", ("How long can a creditor sue me for a debt in Georgia?", "What income is protected from garnishment?", "What should I do if I'm served with a lawsuit?")),
    (r"injur|accident", ("How long do I have to file an injury claim?", "What evidence should I keep after an accident?")),
    (r"small claims|magistrate|sue", ("How do I file in magistrate court?", "How much can I sue for in small claims?")),
)
GENERIC_FOLLOW_UPS = ("What deadlines should I watch for?", "Where can I get free legal help in Georgia?", "What documents should I gather?")


def follow_ups(text: str, n: int = 3) -> list[str]:
    low = (text or "").lower()
    for pattern, items in FOLLOW_UPS:
        if re.search(pattern, low):
            return list(items[:n])
    return list(GENERIC_FOLLOW_UPS[:n])


HELP_LINKS = [
    {"title": "Georgia Legal Aid (Georgia Legal Services Program)", "url": "https://www.glsp.org/"},
    {"title": "Atlanta Legal Aid Society", "url": "https://atlantalegalaid.org/"},
    {"title": "Georgia Courts self-help", "url": "https://georgiacourts.gov/a2j/"},
    {"title": "State Bar of Georgia — find a lawyer", "url": "https://www.gabar.org/public/find-a-lawyer"},
]
