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
    (r"murder|homicide|manslaughter|\bkill(ed|ing)? (someone|somebody|a (man|guy|dude|person)|him|her|them)\b|\bshot (someone|somebody|a (man|guy|dude|person)|him|her|them)\b",
     ("16-3-21", "16-3-24.2", "16-3-23.1", "16-3-20", "16-3-23", "16-5-1", "16-5-2", "16-5-3", "17-6-1")),
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
    # Everyday civil: insurance, fire/property damage, workplace injury, slip-and-fall
    (r"insur|claim (denied|rejected)|coverage|premium|policy", ("33-4-6", "33-7-11", "9-3-33")),
    (r"fire|burn|smoke damage|property damage|house fire|apartment fire", ("51-1-6", "51-12-4", "9-3-31", "44-7-14")),
    (r"workplace|work injury|on the job|workers.?comp|hurt at work|fell at work", ("34-9-1", "34-9-8", "34-9-11", "9-3-33")),
    (r"slip and fall|tripped|wet floor|premises liability", ("51-1-6", "51-3-1", "9-3-33")),
    (r"car insurance|auto insurance|uninsured motorist|um coverage", ("33-7-11", "40-6-10", "9-3-33")),
    (r"medical bill|hospital bill|doctor bill after (accident|wreck|injury)", ("9-3-33", "51-1-6", "51-12-4")),
    (r"restraining order|protective order|tpo|family violence", ("19-13-1", "19-13-3", "19-13-4")),
    (r"hoa|homeowners association|condo association|special assessment", ("44-3-100", "44-3-106", "44-3-109")),
    (r"unemployment|jobless|laid off|severance", ("34-8-1", "34-8-193", "34-8-195")),
    (r"discrimination|harassment|wrongful termination|fired because", ("34-5-1", "34-5-3", "34-7-1")),
    (r"identity theft|stolen identity|credit report|fraudulent account", ("16-9-120", "16-9-121", "10-1-393")),
    (r"student loan|student debt|default on loan", ("9-3-24", "9-3-25", "18-4-5")),
    (r"medical malpractice|doctor mistake|hospital negligence|wrong diagnosis", ("9-3-71", "9-3-73", "51-1-27")),
    (r"guardianship|conservatorship|incapacitated|power of attorney", ("29-4-1", "29-4-10", "29-5-1")),
    (r"adoption|stepparent adoption|terminate parental", ("19-8-1", "19-8-10", "19-8-13")),
    (r"traffic accident|car accident|hit and run|rear end", ("40-6-270", "40-6-49", "9-3-33")),
    (r"parking ticket|parking citation|boot|towed", ("40-6-226", "40-11-2", "15-10-2")),
    (r"consumer fraud|false advertising|bait and switch|refund refused", ("10-1-393", "10-1-399", "13-6-11")),
    (r"landlord repair|habitability|no heat|no water|mold", ("44-7-13", "44-7-14", "44-7-50")),
    (r"foreclosure|mortgage|default on house|short sale", ("44-14-160", "44-14-162", "9-3-24")),
    (r"bankruptcy|chapter 7|chapter 13|discharge debt", ("9-3-24", "18-4-5")),
    (r"neighbor dispute|boundary|easement|tree overhang", ("44-9-1", "51-9-1", "41-1-4")),
    (r"child support modification|change child support|modify support", ("19-6-15", "19-6-19")),
    (r"custody modification|change custody|modify custody", ("19-9-1", "19-9-3")),
    (r"alimony modification|change alimony|modify alimony", ("19-6-19", "19-6-1")),
    (r"name change|change my name|petition to change name", ("19-12-1", "19-12-2")),
    (r"will|probate|estate|inherit|died without a will", ("53-4-20", "53-2-1", "15-9-30")),
    (r"small claims limit|magistrate court limit|how much can I sue", ("15-10-2", "15-10-43")),
    (r"traffic ticket|speeding ticket|red light|points on license", ("40-6-181", "40-13-1", "40-5-57")),
    (r"license suspension|suspended license|reinstatement", ("40-5-57", "40-5-58", "40-5-67.1")),
    (r"expungement|record restriction|seal my record|clear my record", ("35-3-37", "42-8-62", "17-10-21")),
    (r"first offender|first offender act|conditional discharge", ("42-8-60", "42-8-62")),
    (r"probation violation|violated probation|probation revoked", ("42-8-38", "42-8-34.1")),
    (r"self defense|justification|stand your ground|use of force", ("16-3-21", "16-3-24.2", "16-3-23.1")),
    (r"assault|battery|fight|affray", ("16-5-20", "16-5-21", "16-5-23")),
    (r"theft|shoplifting|stolen property", ("16-8-2", "16-8-14", "16-8-7")),
    (r"drug|controlled substance|marijuana|possession", ("16-13-30", "16-13-2")),
    (r"firearm|weapon|gun|carry permit", ("16-11-126", "16-11-127", "16-11-129")),
    (r"dui|driving under the influence|implied consent", ("40-6-391", "40-5-67.1", "40-6-392")),
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


_DOC_PATTERN = r"\bdocuments?\b|\bpapers?\b|\bforms?\b|\bletter\b|\bsummons\b|\bsubpoena"
# Suggested follow-ups. Matched on the user's CURRENT question first (then the answer, except for
# jail/prison), so suggestions stay on the topic asked and never assume custody or a conviction.
FOLLOW_UPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (r"self[- ]defen[cs]e|justification|stand your ground|use of force", ("When does Georgia law treat force as justified?", "How does a pretrial immunity hearing work in Georgia?", "What evidence helps show self-defense?")),
    (r"expung|record restrict|criminal record", ("Which charges can be restricted in Georgia?", "How do I request record restriction from the prosecutor?", "Does First Offender status help a record?")),
    (r"first offender", ("Who is eligible for First Offender treatment?", "What happens after First Offender is completed?")),
    (r"security deposit|deposit back", ("How long does a landlord have to return a deposit?", "Can I sue for a deposit in small claims court?", "What can a landlord deduct from a deposit?")),
    (r"evict|dispossessory|landlord|tenant", ("How much notice does a Georgia landlord have to give?", "What happens at a dispossessory hearing?", "Can a landlord lock a tenant out?")),
    (r"\bdui\b|under the influence|implied consent|license suspen", ("How do I request an ALS hearing with DDS?", "What is an ignition interlock limited permit?", "What happens at a first DUI court date?")),
    (r"traffic|speeding|\bticket|super speeder|points on my license", ("How do points on a Georgia license work?", "Can I contest a traffic ticket in court?", "What happens if I miss my court date for a ticket?")),
    (r"\bappeal|new trial|convicted|conviction", ("How do I file a notice of appeal in Georgia?", "What is a motion for new trial?", "Which court hears my appeal?")),
    (r"custody|visitation|parenting plan", ("What does the court consider for custody in Georgia?", "How do I change a custody order?", "What is a parenting plan?")),
    (r"divorce|alimony|separat", ("How long does an uncontested divorce take?", "How is property divided in a Georgia divorce?", "What are the residency rules to file for divorce in Georgia?")),
    (r"child support", ("How is child support calculated in Georgia?", "How do I change a child support order?")),
    (r"debt|garnish|collector", ("How long can a creditor sue over a debt in Georgia?", "What income is protected from garnishment?", "What should I do if I'm served with a lawsuit?")),
    (r"injur|accident|wreck", ("How long do I have to file an injury claim?", "What evidence should I keep after an accident?", "Can I still recover if I was partly at fault?")),
    (r"insur|claim denied|coverage", ("What should I do if my insurance claim is denied?", "How long do I have to file an insurance claim in Georgia?", "What documents should I keep for an insurance claim?")),
    (r"fire|property damage|smoke", ("What can I recover for fire or property damage?", "How long do I have to sue for property damage in Georgia?", "What evidence should I keep after a fire?")),
    (r"workplace|work injury|workers.?comp|hurt at work", ("Do I have to report a work injury right away?", "What does workers' compensation cover in Georgia?", "Can I sue my employer for a work injury?")),
    (r"slip and fall|tripped|wet floor|premises", ("What do I have to prove in a slip-and-fall case?", "How long do I have to file a premises liability claim?", "What evidence helps a slip-and-fall claim?")),
    (r"car insurance|auto insurance|uninsured", ("What does uninsured motorist coverage do in Georgia?", "Do I have to report a car accident to my insurance?", "What if the other driver has no insurance?")),
    (r"medical bill|hospital bill", ("Can I recover medical bills after an accident?", "What if my health insurance paid some of the bills?", "How long do I have to claim medical expenses?")),
    (r"restraining order|protective order|tpo|family violence", ("How do I get a temporary protective order in Georgia?", "What happens at a TPO hearing?", "How long does a protective order last?")),
    (r"hoa|homeowners association|condo", ("What can an HOA enforce in Georgia?", "Can I challenge an HOA fine or assessment?", "What are my rights if the HOA won't make repairs?")),
    (r"unemployment|laid off|jobless", ("How do I file for unemployment in Georgia?", "What if my unemployment claim is denied?", "How long can I receive unemployment benefits?")),
    (r"discrimination|harassment|wrongful termination", ("What counts as workplace discrimination in Georgia?", "How do I report harassment at work?", "What should I do if I was fired unfairly?")),
    (r"identity theft|stolen identity|credit report", ("What should I do if someone stole my identity?", "How do I dispute a fraudulent charge?", "Can I freeze my credit in Georgia?")),
    (r"student loan|student debt", ("How long can a student loan collector sue in Georgia?", "What happens if I default on a student loan?", "Can student loans be discharged in bankruptcy?")),
    (r"medical malpractice|doctor mistake|hospital", ("How long do I have to sue for medical malpractice in Georgia?", "What do I have to prove in a malpractice case?", "Do I need an expert affidavit?")),
    (r"guardianship|conservatorship|power of attorney", ("How do I get guardianship of an adult in Georgia?", "What is the difference between guardianship and power of attorney?", "How do I challenge a guardianship?")),
    (r"adoption|stepparent", ("How does stepparent adoption work in Georgia?", "What are the steps to adopt a child?", "Can parental rights be terminated?")),
    (r"traffic accident|car accident|hit and run", ("What should I do right after a car accident?", "Do I have to call the police?", "How long do I have to sue after a car wreck?")),
    (r"parking ticket|boot|towed", ("How do I contest a parking ticket?", "What can I do if my car was booted or towed?", "Can I sue for an illegal tow?")),
    (r"consumer fraud|false advertising|refund", ("What is consumer fraud in Georgia?", "How do I get a refund for a deceptive sale?", "Can I sue in small claims for consumer fraud?")),
    (r"landlord repair|habitability|mold|no heat", ("What repairs is a landlord required to make?", "Can I withhold rent if the landlord won't fix things?", "How do I force a landlord to make repairs?")),
    (r"foreclosure|mortgage|short sale", ("How does foreclosure work in Georgia?", "Can I stop a foreclosure?", "What is a short sale?")),
    (r"bankruptcy|chapter 7|chapter 13", ("What is the difference between Chapter 7 and Chapter 13?", "What debts can be discharged in bankruptcy?", "How do I file for bankruptcy in Georgia?")),
    (r"neighbor dispute|boundary|easement|tree", ("How do I resolve a boundary dispute?", "What can I do about a neighbor's tree?", "What is an easement?")),
    (r"child support modification|change child support", ("How do I change a child support order?", "What counts as a change in circumstances?", "How is child support recalculated?")),
    (r"custody modification|change custody", ("How do I change a custody order?", "What does the court consider for a custody change?", "How long does a custody modification take?")),
    (r"alimony modification|change alimony", ("How do I change an alimony order?", "What is a substantial change in circumstances?", "Can alimony be terminated?")),
    (r"name change|change my name", ("How do I change my name in Georgia?", "What do I need for a name change petition?", "How long does a name change take?")),
    (r"will|probate|estate|inherit", ("Do I need a will in Georgia?", "What happens if someone dies without a will?", "How does probate work?")),
    (r"small claims|magistrate court limit", ("What is the small claims limit in Georgia?", "How do I file in magistrate court?", "What if the amount is over the limit?")),
    (r"traffic ticket|speeding|red light|points", ("How do points on a Georgia license work?", "Can I contest a traffic ticket?", "What happens if I miss my court date?")),
    (r"license suspension|suspended license", ("How do I reinstate a suspended license?", "What is a limited permit?", "How long does a suspension last?")),
    (r"expungement|record restriction|seal my record", ("Which charges can be restricted in Georgia?", "How do I request record restriction?", "Does First Offender help?")),
    (r"first offender|conditional discharge", ("Who is eligible for First Offender?", "What happens after First Offender is completed?", "Can First Offender be revoked?")),
    (r"probation violation|violated probation", ("What happens if I violate probation?", "Can probation be revoked?", "What should I do if I get a probation violation?")),
    (r"self defense|stand your ground|justification", ("When is force justified in Georgia?", "How does a pretrial immunity hearing work?", "What evidence helps show self-defense?")),
    (r"assault|battery|fight", ("What is the difference between assault and battery?", "What are the penalties?", "Can I claim self-defense?")),
    (r"theft|shoplifting|stolen", ("What is the difference between theft and shoplifting?", "What are the penalties for theft?", "Can theft charges be restricted?")),
    (r"drug|controlled substance|marijuana|possession", ("What are the penalties for possession?", "Can drug charges be restricted?", "What is a conditional discharge for drugs?")),
    (r"firearm|weapon|gun|carry", ("Do I need a permit to carry in Georgia?", "What are the rules for carrying a firearm?", "What happens if I carry in a prohibited place?")),
    (r"dui|driving under the influence", ("What are the penalties for a first DUI?", "How do I request an ALS hearing?", "What is an ignition interlock permit?")),
    (r"small claims|magistrate|\bsue\b", ("How do I file in magistrate court?", "How much can I sue for in small claims?")),
    (r"\bbond\b|\bbail\b", ("How is bond set in Georgia?", "Can a bond amount be reduced?")),
    # "searched without a warrant" is about a search, not an arrest warrant.
    (r"(?<!without a )(?<!no )(?<!a search )\bwarrant(?!less)", ("How can I check if there is a warrant?", "What happens after a warrant is served?")),
    (_DOC_PATTERN, ("What does this document mean?", "Is there a deadline in this document?", "What questions should I ask a lawyer about it?")),
)
# Jail/prison follow-ups only when the user's own current question is explicitly about custody or conditions.
PRISON_FOLLOW_UPS = ("How do I file a grievance in a Georgia prison or jail?", "How can family report conditions to the Georgia Department of Corrections?", "Where can someone in custody get free legal help?")
_WRAPPER_RE = re.compile(r"(?:^|\n)User:[ \t]*")


def current_question(text: str) -> str:
    """The user's latest message. App clients wrap it in a preamble plus history ending in 'User: ...';
    the preamble (which mentions incarceration as an in-scope topic) must not drive topic detection."""
    t = text or ""
    parts = _WRAPPER_RE.split(t)
    return parts[-1].strip() if len(parts) > 1 else t.strip()


def follow_ups(question: str, answer: str = "", n: int = 3) -> list[str]:
    """Topic-specific suggestions for the current question, or [] when nothing relevant fits."""
    q = current_question(question).lower()
    if re.search(PRISON, q):
        return list(PRISON_FOLLOW_UPS[:n])
    from .defense_help import is_broad_defense, BROAD_FOLLOW_UPS
    if is_broad_defense(q):
        return list(BROAD_FOLLOW_UPS[:n])
    for text, from_answer in ((q, False), ((answer or "").lower(), True)):
        if from_answer:
            from .defense_help import is_criminal, CHARGE_FOLLOW_UPS, _allowed_stages, _PRE
            if is_criminal(q) and _allowed_stages(q) == _PRE:
                return list(CHARGE_FOLLOW_UPS[:n])
        for pattern, items in FOLLOW_UPS:
            if from_answer and pattern == _DOC_PATTERN:
                continue  # answers mention documents generically; only the question can pick this topic
            if re.search(pattern, text):
                return [i for i in items if i.lower().rstrip("?") != q.rstrip("?")][:n]
    return []


HELP_LINKS = [
    {"title": "Georgia Legal Aid (Georgia Legal Services Program)", "url": "https://www.glsp.org/"},
    {"title": "Atlanta Legal Aid Society", "url": "https://atlantalegalaid.org/"},
    {"title": "Georgia Courts self-help", "url": "https://georgiacourts.gov/a2j/"},
    {"title": "State Bar of Georgia — find a lawyer", "url": "https://www.gabar.org/public/find-a-lawyer"},
]
