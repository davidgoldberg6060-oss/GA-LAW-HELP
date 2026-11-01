"""Hand-written map of common legal slang / street language -> plain legal search words.

Used only to widen retrieval (search terms and topic lookups). It never changes what the
user said and never becomes legal text.
"""
from __future__ import annotations
import re

SLANG: tuple[tuple[str, str], ...] = (
    (r"caught a body|catch(ing)? a body|\bbodied\b|smoked (him|her|them|somebody|someone|a (dude|man|guy))|dropped (him|her|them|somebody|someone)|\bmerked\b|\bwhacked\b|\bpopped (him|her|them|somebody|someone)\b|lit (him|her|them) up", "killed someone homicide murder"),
    (r"locked up|lock(ed)? me up|booked|jail ?time|in jail|behind bars|catch(ing)? a case|caught a case", "arrest criminal charge sentence"),
    (r"(i'?m|i am|currently|been|still) (in|locked up in|stuck in) (prison|jail|a cell)|incarcerat|\binmates?\b|\bmy cell\b|cell ?block|\bco'?s\b|\bguards?\b|solitary|the hole|commissary|grievance|state pen", "inmate prison conditions sheriff corrections"),
    (r"no (water|food|bed|mattress|blanket|medical|doctor|meds|medication)|not feeding|starv|denied (medical|my meds)", "necessities food water medical treatment"),
    (r"\bpopped\b|\bcaught\b|\bbusted\b|got arrested|picked up by", "arrest"),
    (r"\bjumped\b|\bscrap(ped|ping)?\b|\bfade\b|\bbeef\b|squabble|\bfight\b|\bfought\b|\bthrew hands\b|\bswung on\b|\bhit me\b|\bpunch(ed)?\b", "fight battery assault affray"),
    (r"defend(ing|ed)? my ?self|self[- ]?defen[cs]e|stand (my|your) ground|protect(ing|ed)? my ?self", "self defense justification use of force"),
    (r"\bstrap(ped)?\b|\bblick\b|\bpole\b|\bglizzy\b|\bheat\b|\bpiece\b|\bburner\b|\bgun\b|\bfirearm\b", "firearm weapon carry"),
    (r"\bweed\b|\bloud\b|\bgas\b|\bza+\b|\bkush\b|\bblunt\b|\bpot\b|\bcannabis\b|marijuana", "marijuana controlled substance possession"),
    (r"\bplug\b|\btrap( house)?\b|\bserving\b|\bslang(ing)?\b|\bselling (dope|drugs|work)\b|\bwork\b.*\bsell", "sale distribution controlled substance"),
    (r"hit a lick|\blick\b|\brobbed\b|\bjack(ed)?\b|\bstick ?up\b", "robbery theft"),
    (r"\bboost(ing|ed)?\b|\bshoplift(ing|ed)?\b|\bswip(ed|ing)\b from (a )?store", "shoplifting theft"),
    (r"\b12\b|\bopps\b|\bfeds\b|\bthe law\b|\bcops?\b|\bpolice\b|\bjakes?\b|\bpigs\b", "police officer law enforcement"),
    (r"\bP\.?O\.?\b|\bviolated\b|\bvop\b|probation", "probation violation revocation"),
    (r"bond(ed)? out|bail(ed)? out|\bbond\b|\bbail\b", "bail bond release"),
    (r"warrant out|got a warrant|\bwarrant\b", "arrest warrant"),
    (r"\bdui\b|\bdwi\b|drunk driv|driving drunk|\bbuzzed\b|\btipsy\b.*driv", "driving under the influence DUI"),
    (r"\bBM\b|baby ?mama|baby ?daddy|\bBD\b|my kids? (mom|mother|dad|father)", "child custody child support visitation"),
    (r"put out|kicked out|evict|thrown out of (my|the) (house|apartment|place)", "eviction dispossessory landlord tenant"),
    (r"\brepo(ssess(ed|ion)?)?\b|took my car back", "repossession secured creditor"),
    (r"car got towed|\btowed\b|\btow(ing)? company\b", "towing vehicle impound"),
    (r"traffic ticket|speeding ticket|\bticket\b|\bcitation\b", "traffic citation"),
    (r"(didn'?t|won'?t|not) pa(y|id) me|owe me (my )?(wages|money)|stiffed|wage theft|final paycheck", "unpaid wages employer"),
    (r"car (wreck|accident)|got hit by a car|fender bender|\bwreck\b", "motor vehicle accident negligence injury"),
    (r"bill collector|debt collector|collections? (agency|calling)", "debt collection"),
    (r"expunge|clear my record|record (sealed|restriction)", "record restriction expungement"),
)
_COMPILED = tuple((re.compile(p, re.I), terms) for p, terms in SLANG)


def plain_terms(text: str) -> str:
    """Plain legal search words implied by slang in ``text`` ('' when none)."""
    out: dict[str, None] = {}
    for pattern, terms in _COMPILED:
        if pattern.search(text or ""):
            out[terms] = None
    return " ".join(out)
