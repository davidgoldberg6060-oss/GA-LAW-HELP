"""Motion/remedy registry primitives for GA.LAW.HELP.

The registry is deliberately evidence-based: discovery does not equal verification.
A motion/remedy may only be presented as verified when backed by a current,
traceable legal authority in the indexed corpus.
"""
from dataclasses import dataclass, asdict
from typing import Iterable

VERIFIED_STATUSES = {"VERIFIED", "OFFICIAL", "CURRENT"}
HISTORICAL_STATUSES = {"HISTORICAL", "SUPERSEDED"}


@dataclass(frozen=True)
class MotionCandidate:
    name: str
    aliases: tuple[str, ...] = ()
    practice_area: str = "criminal"
    stage: str = "unknown"
    purpose: str = ""


# Initial canonical taxonomy. This is a seed, not a claim of exhaustive coverage.
# Additional candidates should be discovered from statutes, rules and opinions.
GEORGIA_MOTION_SEED: tuple[MotionCandidate, ...] = (
    MotionCandidate("Motion to Suppress Evidence", ("motion to suppress",), "criminal", "pretrial", "Challenge unlawfully obtained evidence."),
    MotionCandidate("Motion to Suppress Statement", ("motion to suppress confession", "motion to suppress statements"), "criminal", "pretrial", "Challenge admissibility of a defendant statement."),
    MotionCandidate("Motion in Limine", (), "criminal/civil", "pretrial", "Seek an advance evidentiary ruling."),
    MotionCandidate("Motion for Continuance", (), "criminal/civil", "pretrial/trial", "Request additional time."),
    MotionCandidate("Motion to Sever", ("motion for severance",), "criminal", "pretrial", "Seek separate trials of defendants or counts when legally available."),
    MotionCandidate("Motion to Dismiss", (), "criminal/civil", "pretrial", "Seek dismissal on an applicable legal ground."),
    MotionCandidate("Motion for Directed Verdict", (), "criminal/civil", "trial", "Challenge legal sufficiency at trial when procedurally available."),
    MotionCandidate("Motion for New Trial", (), "criminal/civil", "post-trial", "Seek a new trial on preserved or otherwise cognizable grounds."),
    MotionCandidate("Motion to Withdraw Guilty Plea", ("motion to withdraw plea",), "criminal", "plea/post-plea", "Seek withdrawal of a guilty plea when legally available."),
    MotionCandidate("Motion to Modify Sentence", ("motion for sentence modification",), "criminal", "sentencing/post-sentence", "Seek lawful sentence modification when jurisdiction and timing permit."),
    MotionCandidate("Extraordinary Motion for New Trial", (), "criminal/civil", "post-trial", "Seek extraordinary new-trial relief when authorized."),
    MotionCandidate("Motion for Reconsideration", (), "criminal/civil", "post-ruling", "Ask a court to reconsider a ruling when procedurally recognized."),
)


def normalize_motion_name(value: str) -> str:
    return " ".join((value or "").lower().replace("-", " ").split())


def seed_catalog() -> list[dict]:
    return [asdict(item) for item in GEORGIA_MOTION_SEED]


def classify_verification(authority_statuses: Iterable[str], has_official_source: bool) -> str:
    statuses = {str(value or "").upper() for value in authority_statuses}
    if has_official_source and statuses & VERIFIED_STATUSES:
        return "VERIFIED_CURRENT"
    if statuses & HISTORICAL_STATUSES:
        return "VERIFIED_HISTORICAL"
    if statuses:
        return "NEEDS_VERIFICATION"
    return "UNRECOGNIZED_RESEARCH_REQUIRED"


def coverage_summary(records: Iterable[dict]) -> dict:
    counts = {
        "VERIFIED_CURRENT": 0,
        "VERIFIED_HISTORICAL": 0,
        "NEEDS_VERIFICATION": 0,
        "UNRECOGNIZED_RESEARCH_REQUIRED": 0,
    }
    total = 0
    for record in records:
        total += 1
        status = str(record.get("verification_status", "UNRECOGNIZED_RESEARCH_REQUIRED"))
        if status not in counts:
            status = "NEEDS_VERIFICATION"
        counts[status] += 1
    return {"identified": total, **counts}
