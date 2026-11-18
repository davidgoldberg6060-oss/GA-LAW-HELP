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
    (r"mutual self.defense|both claim self.defense|both people self.defense|mutual combat|both claim immunity|two people fought|both thought the other", ("16-3-21", "16-3-24.2", "16-5-20", "16-11-32")),
    (r"affray|mutual fight|public fight|both charged after fight", ("16-11-32", "16-5-23", "16-5-20")),
    (r"pretrial immunity|immunity hearing|motion for immunity", ("16-3-24.2", "16-3-21")),
    (r"dismiss charges|get charges dropped|nolle prosequi|nol pros", ("17-8-3", "17-7-70.1")),
    (r"plea bargain|reduce charge|lesser included", ("17-10-1", "16-1-6")),
    (r"self defense claim|claim self defense|assert self defense", ("16-3-21", "16-3-24.2")),
    (r"reasonable fear|imminent harm|imminent threat", ("16-3-21", "16-3-20")),
    (r"initial aggressor|who started the fight|provoked", ("16-3-21", "16-5-20")),
    (r"assault|battery|fight|affray", ("16-5-20", "16-5-21", "16-5-23")),
    (r"theft|shoplifting|stolen property", ("16-8-2", "16-8-14", "16-8-7")),
    (r"drug|controlled substance|marijuana|possession", ("16-13-30", "16-13-2")),
    (r"firearm|weapon|gun|carry permit", ("16-11-126", "16-11-127", "16-11-129")),
    (r"dui|driving under the influence|implied consent", ("40-6-391", "40-5-67.1", "40-6-392")),
    (r"bond|bail|bond reduction|cash bond", ("17-6-1", "17-6-2")),
    (r"warrant|arrest warrant|search warrant", ("17-4-40", "17-4-20")),
    (r"appeal|notice of appeal|new trial", ("5-6-34", "5-5-40", "5-5-41")),
    (r"habeas|habeas corpus|post conviction", ("9-14-1", "9-14-42")),
    (r"contempt|contempt of court|failure to appear", ("15-1-4", "17-7-90")),
    (r"restitution|pay back|victim restitution", ("17-14-1", "17-14-10")),
    (r"community service|work alternative", ("42-8-34", "42-8-60")),
    (r"eviction|dispossessory|landlord tenant|notice to quit", ("44-7-50", "44-7-51", "44-7-53")),
    (r"security deposit|deposit return|landlord deposit", ("44-7-30", "44-7-33", "44-7-34")),
    (r"child custody|visitation|parenting plan", ("19-9-1", "19-9-3")),
    (r"child support calculation|how is child support calculated", ("19-6-15",)),
    (r"divorce residency|how long to live in georgia for divorce", ("19-5-2", "19-5-1")),
    (r"alimony|spousal support|temporary alimony", ("19-6-1", "19-6-3")),
    (r"debt collection|collector|garnishment|wage garnishment", ("18-4-1", "18-4-5", "9-3-24")),
    (r"contract breach|breach of contract|warranty", ("13-1-1", "13-6-11", "9-3-24")),
    (r"small claims filing|how to file in magistrate", ("15-10-43", "15-10-2")),
    (r"insurance claim denied|bad faith insurance", ("33-4-6", "33-7-11")),
    (r"workers compensation claim|file workers comp", ("34-9-8", "34-9-11")),
    (r"slip and fall lawsuit|premises liability claim", ("51-3-1", "51-1-6")),
    (r"car wreck lawsuit|personal injury lawsuit", ("9-3-33", "51-1-6")),
    (r"overtime|unpaid overtime|final paycheck|wage theft", ("34-4-3", "34-7-2")),
    (r"fired|wrongful discharge|at will employment", ("34-7-1",)),
    (r"consumer protection|fair business practices|deceptive practices", ("10-1-393", "10-1-399")),
    (r"lemon law|car dealer|defective car", ("10-1-780", "10-1-782")),
    (r"credit report dispute|credit error|identity theft report", ("16-9-120", "10-1-393")),
    (r"protective order enforcement|violation of tpo", ("19-13-6", "19-13-4")),
    (r"no contact order|stay away order|restraining", ("19-13-1", "19-13-4")),
    (r"domestic violence|family violence act|abuse", ("19-13-1", "19-13-3")),
    (r"child abuse|neglect|dfcs|cps", ("19-7-5", "15-11-2")),
    (r"juvenile|delinquent|status offense", ("15-11-2", "15-11-601")),
    (r"traffic stop|pulled over|license and registration", ("40-5-29", "40-6-10")),
    (r"accident report|police report|hit and run report", ("40-6-270", "40-6-273")),
    (r"uninsured motorist claim|um claim|hit by uninsured", ("33-7-11", "40-6-10")),
    (r"property damage claim|car repair|totaled car", ("51-12-4", "9-3-31")),
    (r"pain and suffering|emotional distress|loss of consortium", ("51-12-4", "51-12-6")),
    (r"statute of limitations|how long to sue|deadline to file", ("9-3-33", "9-3-24", "9-3-71")),
    (r"service of process|served papers|summons", ("9-11-4", "9-11-5")),
    (r"default judgment|didn't answer|missed deadline", ("9-11-55", "9-11-60")),
    (r"discovery|interrogatories|deposition", ("9-11-26", "9-11-30")),
    (r"settlement|mediation|negotiate", ("9-11-68", "15-19-10")),
    (r"attorney fees|lawyer fees|contingency", ("13-6-11", "9-15-14")),
    (r"court costs|filing fee|cost of suit", ("9-15-1", "15-6-77")),
    (r"judgment enforcement|collect judgment|garnish judgment", ("9-12-60", "18-4-1")),
    (r"appeal bond|supersedeas|stay pending appeal", ("5-6-46", "5-6-47")),
    (r"motion to dismiss|12b6|failure to state a claim", ("9-11-12",)),
    (r"summary judgment|no genuine issue", ("9-11-56",)),
    (r"jury trial|bench trial|demand jury", ("9-11-38", "9-11-39")),
    (r"subpoena|witness subpoena|document subpoena", ("24-13-21", "24-13-26")),
    (r"expert witness|expert testimony|affidavit", ("24-7-702", "9-11-56")),
    (r"continuance|postpone hearing|reschedule", ("9-10-150", "17-8-22")),
    (r"plea bargain|plea deal|guilty plea", ("17-7-93", "17-10-1")),
    (r"nolo contendere|no contest|first offender plea", ("17-7-95", "42-8-60")),
    (r"probation terms|probation conditions|special conditions", ("42-8-34", "42-8-35")),
    (r"early termination of probation|terminate probation early", ("42-8-34", "42-8-60")),
    (r"parole|parole board|parole eligibility", ("42-9-1", "42-9-42")),
    (r"pardon|clemency|commutation", ("42-9-1", "42-9-20")),
    (r"record restriction eligibility|what charges can be restricted", ("35-3-37", "42-8-62")),
    (r"arrest record|booking|mugshot", ("35-3-37", "17-4-20")),
    (r"bond forfeiture|forfeited bond|bond revoked", ("17-6-31", "17-6-70")),
    (r"failure to appear|fta|bench warrant", ("17-6-12", "17-4-40")),
    (r"public defender|appointed counsel|indigent", ("17-12-1", "17-12-23")),
    (r"child support enforcement|dcss|contempt for support", ("19-6-15", "19-6-28")),
    (r"visitation denial|denied visitation|interference with visitation", ("19-9-3", "19-9-1")),
    (r"relocation|move with child|move out of state", ("19-9-3", "19-9-1")),
    (r"paternity|establish paternity|legitimation", ("19-7-22", "19-7-43")),
    (r"grandparent visitation|grandparents rights", ("19-7-3",)),
    (r"emancipation|emancipate minor", ("19-7-1", "15-11-2")),
    (r"name change for child|change child's name", ("19-12-1", "19-12-2")),
    (r"divorce papers|served divorce|divorce complaint", ("19-5-1", "9-11-4")),
    (r"answer divorce|respond to divorce|divorce answer", ("19-5-1", "9-11-12")),
    (r"temporary orders|temporary custody|temporary support", ("19-6-3", "19-9-1")),
    (r"final decree|divorce decree|judgment of divorce", ("19-5-1", "19-5-12")),
    (r"property division|equitable division|marital property", ("19-5-13", "19-5-1")),
    (r"separate property|non-marital|premarital", ("19-5-13",)),
    (r"debt division|who pays debts|marital debt", ("19-5-13", "19-5-1")),
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
    (r"mutual self.defense|both claim self.defense|both people|mutual combat|both claim immunity|two people fought", ("Can both people in a fight claim self-defense?", "How does a court decide when both claim immunity?", "What is mutual combat under Georgia law?")),
    (r"dismiss charges|get charges dropped|nolle", ("How can charges be dismissed in Georgia?", "What is a nolle prosequi?", "Can the prosecutor drop charges?")),
    (r"plea bargain|reduce charge|lesser", ("How do plea bargains work in Georgia?", "Can a charge be reduced?", "What is a lesser included offense?")),
    (r"reasonable fear|imminent harm|imminent threat", ("What counts as reasonable fear?", "How do I show I faced imminent harm?", "What evidence helps a self-defense claim?")),
    (r"initial aggressor|who started|provoked", ("What if I started the fight?", "Can an initial aggressor claim self-defense?", "What is the withdrawal rule?")),
    (r"affray|mutual fight|public fight", ("What is an affray?", "Can both people be charged after a fight?", "How is an affray different from battery?")),
    (r"pretrial immunity|immunity hearing", ("How do I request a pretrial immunity hearing?", "What do I have to prove for immunity?", "What happens if immunity is granted?")),
    (r"assault|battery|fight", ("What is the difference between assault and battery?", "What are the penalties?", "Can I claim self-defense?")),
    (r"theft|shoplifting|stolen", ("What is the difference between theft and shoplifting?", "What are the penalties for theft?", "Can theft charges be restricted?")),
    (r"drug|controlled substance|marijuana|possession", ("What are the penalties for possession?", "Can drug charges be restricted?", "What is a conditional discharge for drugs?")),
    (r"firearm|weapon|gun|carry", ("Do I need a permit to carry in Georgia?", "What are the rules for carrying a firearm?", "What happens if I carry in a prohibited place?")),
    (r"dui|driving under the influence", ("What are the penalties for a first DUI?", "How do I request an ALS hearing?", "What is an ignition interlock permit?")),
    (r"bond|bail|bond reduction", ("How is bond set in Georgia?", "Can I get a bond reduction?", "What is a cash bond?")),
    (r"warrant|arrest warrant|search warrant", ("How can I check if there is a warrant?", "What happens after a warrant is served?", "Can I challenge a search warrant?")),
    (r"appeal|notice of appeal|new trial", ("How do I file a notice of appeal?", "What is a motion for new trial?", "How long do I have to appeal?")),
    (r"habeas|post conviction", ("What is a habeas corpus petition?", "When can I file for habeas?", "What are the deadlines for habeas?")),
    (r"contempt|failure to appear", ("What is contempt of court?", "What happens if I miss court?", "How do I fix a failure to appear?")),
    (r"restitution|pay back", ("What is restitution?", "How is restitution calculated?", "What if I can't pay restitution?")),
    (r"community service", ("How does community service work?", "Can I do community service instead of jail?", "What counts as community service?")),
    (r"eviction|dispossessory|notice to quit", ("How much notice does a landlord have to give?", "What happens at a dispossessory hearing?", "Can a landlord lock me out?")),
    (r"security deposit|deposit return", ("How long does a landlord have to return a deposit?", "What can a landlord deduct?", "Can I sue for a deposit?")),
    (r"child custody|visitation|parenting", ("What does the court consider for custody?", "How do I get a parenting plan?", "How do I change visitation?")),
    (r"child support calculation", ("How is child support calculated?", "What income is counted?", "How do I change child support?")),
    (r"divorce residency", ("How long do I have to live in Georgia to file for divorce?", "What are the grounds for divorce?", "How long does an uncontested divorce take?")),
    (r"alimony|spousal support", ("How is alimony decided?", "Can alimony be temporary?", "How do I change alimony?")),
    (r"debt collection|garnishment|collector", ("How long can a creditor sue?", "What income is protected from garnishment?", "What should I do if I'm served?")),
    (r"contract breach|warranty", ("What is a breach of contract?", "How long do I have to sue on a contract?", "What damages can I recover?")),
    (r"small claims filing|magistrate", ("How do I file in magistrate court?", "What is the filing fee?", "What if the other side doesn't show up?")),
    (r"insurance claim denied|bad faith", ("What should I do if my claim is denied?", "What is bad faith insurance?", "How long do I have to sue an insurance company?")),
    (r"workers compensation claim|workers comp", ("How do I file a workers' comp claim?", "What does workers' comp cover?", "Can I sue my employer instead?")),
    (r"slip and fall|premises liability", ("What do I have to prove?", "How long do I have to file?", "What evidence should I keep?")),
    (r"car wreck|personal injury", ("How long do I have to sue after a car wreck?", "What if I was partly at fault?", "What damages can I recover?")),
    (r"overtime|unpaid overtime|final paycheck|wage theft", ("Am I owed overtime?", "How do I claim unpaid wages?", "What is the deadline for a wage claim?")),
    (r"fired|wrongful discharge|at will", ("Can I be fired for any reason?", "What is wrongful discharge?", "What should I do if I was fired?")),
    (r"consumer protection|deceptive practices", ("What is a deceptive practice?", "How do I report a business?", "Can I sue for consumer fraud?")),
    (r"lemon law|defective car", ("Does Georgia have a lemon law?", "What if my new car is defective?", "How do I pursue a lemon law claim?")),
    (r"credit report|credit error", ("How do I dispute a credit report error?", "What if someone opened an account in my name?", "How do I freeze my credit?")),
    (r"protective order enforcement|violation of tpo", ("What happens if someone violates a TPO?", "How do I report a violation?", "Can a TPO be extended?")),
    (r"no contact|stay away|restraining", ("How do I get a no-contact order?", "What happens if it is violated?", "How long does it last?")),
    (r"domestic violence|family violence|abuse", ("How do I get a protective order?", "What is the Family Violence Act?", "Where can I get help?")),
    (r"child abuse|neglect|dfcs", ("What should I do if I suspect child abuse?", "What is DFCS?", "What are my rights if DFCS is involved?")),
    (r"juvenile|delinquent|status offense", ("What happens in juvenile court?", "What is a status offense?", "Can a juvenile record be restricted?")),
    (r"traffic stop|pulled over", ("What should I do during a traffic stop?", "Do I have to show my license?", "Can I refuse a search?")),
    (r"accident report|police report", ("Do I have to file an accident report?", "How do I get a copy of the police report?", "What if the other driver left?")),
    (r"uninsured motorist|um claim|hit by uninsured", ("What is uninsured motorist coverage?", "How do I file a UM claim?", "What if the other driver has no insurance?")),
    (r"property damage|car repair|totaled", ("How is property damage calculated?", "What if my car is totaled?", "Can I recover rental car costs?")),
    (r"pain and suffering|emotional distress", ("Can I recover for pain and suffering?", "What is loss of consortium?", "How are non-economic damages calculated?")),
    (r"statute of limitations|how long to sue|deadline", ("How long do I have to sue?", "What is the statute of limitations for injury?", "What if I miss the deadline?")),
    (r"service of process|served papers|summons", ("What does it mean to be served?", "What should I do if I am served?", "How long do I have to answer?")),
    (r"default judgment|didn't answer|missed", ("What is a default judgment?", "Can I set aside a default?", "What if I missed the deadline to answer?")),
    (r"discovery|interrogatories|deposition", ("What is discovery?", "Do I have to answer interrogatories?", "What happens at a deposition?")),
    (r"settlement|mediation|negotiate", ("Should I settle?", "What is mediation?", "Can I negotiate myself?")),
    (r"attorney fees|lawyer fees|contingency", ("Can I recover attorney fees?", "What is a contingency fee?", "Who pays the lawyer?")),
    (r"court costs|filing fee", ("What are the filing fees?", "Who pays court costs?", "Can costs be waived?")),
    (r"judgment enforcement|collect judgment", ("How do I collect a judgment?", "Can I garnish wages for a judgment?", "How long is a judgment good for?")),
    (r"appeal bond|supersedeas", ("What is an appeal bond?", "Do I have to post a bond to appeal?", "What is a supersedeas?")),
    (r"motion to dismiss|12b6", ("What is a motion to dismiss?", "What is failure to state a claim?", "How do I respond to a motion to dismiss?")),
    (r"summary judgment", ("What is summary judgment?", "When can summary judgment be granted?", "How do I oppose summary judgment?")),
    (r"jury trial|bench trial", ("Do I have a right to a jury trial?", "What is the difference between jury and bench trial?", "How do I demand a jury?")),
    (r"subpoena|witness", ("How do I subpoena a witness?", "What if someone ignores a subpoena?", "Can I subpoena documents?")),
    (r"expert witness|expert testimony", ("Do I need an expert?", "What is an expert affidavit?", "How do I challenge an expert?")),
    (r"continuance|postpone|reschedule", ("How do I ask for a continuance?", "What are good reasons for a continuance?", "Can the other side oppose it?")),
    (r"plea bargain|plea deal|guilty plea", ("Should I take a plea?", "What is a plea bargain?", "What happens at a plea hearing?")),
    (r"nolo contendere|no contest", ("What is nolo contendere?", "Is nolo the same as guilty?", "Can nolo be used against me later?")),
    (r"probation terms|conditions", ("What are typical probation conditions?", "What happens if I violate a condition?", "Can conditions be changed?")),
    (r"early termination of probation", ("Can I end probation early?", "How do I request early termination?", "What does the judge consider?")),
    (r"parole|parole board", ("When am I eligible for parole?", "How does the parole board decide?", "What happens at a parole hearing?")),
    (r"pardon|clemency|commutation", ("How do I apply for a pardon?", "What is clemency?", "Who grants pardons in Georgia?")),
    (r"record restriction eligibility", ("Which charges can be restricted?", "How do I apply for restriction?", "Does restriction remove the record completely?")),
    (r"arrest record|booking|mugshot", ("Can I get my arrest record restricted?", "What is a booking record?", "How do I get a mugshot removed?")),
    (r"bond forfeiture|forfeited bond", ("What happens if I forfeit bond?", "Can a forfeited bond be set aside?", "What is a bond revocation?")),
    (r"failure to appear|fta|bench warrant", ("What happens if I miss court?", "How do I clear a failure to appear?", "What is a bench warrant?")),
    (r"public defender|appointed counsel|indigent", ("How do I get a public defender?", "What if I want to fire my public defender?", "Am I eligible for appointed counsel?")),
    (r"child support enforcement|dcss|contempt for support", ("What is DCSS?", "How do I enforce child support?", "What is contempt for non-payment?")),
    (r"visitation denial|denied visitation", ("What can I do if visitation is denied?", "How do I enforce a visitation order?", "Can I file for contempt?")),
    (r"relocation|move with child|move out of state", ("Do I need permission to move with my child?", "How do I ask the court to relocate?", "What does the court consider?")),
    (r"paternity|establish paternity|legitimation", ("How do I establish paternity?", "What is legitimation?", "How does paternity affect support and custody?")),
    (r"grandparent visitation|grandparents", ("Can grandparents get visitation?", "What do grandparents have to prove?", "How do I file for grandparent visitation?")),
    (r"emancipation|emancipate", ("How can a minor become emancipated?", "What are the requirements?", "What rights does emancipation give?")),
    (r"name change for child|change child's name", ("How do I change my child's name?", "Do both parents have to agree?", "What does the court consider?")),
    (r"divorce papers|served divorce", ("What should I do if I am served with divorce papers?", "How long do I have to answer?", "What is a divorce complaint?")),
    (r"answer divorce|respond to divorce", ("How do I answer a divorce complaint?", "What if I don't answer?", "Do I need a lawyer to answer?")),
    (r"temporary orders|temporary custody|temporary support", ("What are temporary orders?", "How do I get temporary custody or support?", "How long do temporary orders last?")),
    (r"final decree|divorce decree", ("What is a final divorce decree?", "What does the decree include?", "Can a decree be changed later?")),
    (r"property division|equitable division|marital property", ("How is property divided in Georgia?", "What is equitable division?", "What is marital property?")),
    (r"separate property|premarital", ("What is separate property?", "Does separate property get divided?", "How do I prove something is separate?")),
    (r"debt division|marital debt", ("Who pays the debts in a divorce?", "Are all debts divided?", "What if my spouse ran up debt?")),
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
