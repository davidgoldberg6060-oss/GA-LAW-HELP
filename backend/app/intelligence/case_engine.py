from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Iterable, Optional

class FindingStatus(str, Enum):
    SUPPORTED = "supported"
    POTENTIAL = "potential_issue"
    NEEDS_INFO = "more_information_required"
    PROCEDURAL_RISK = "likely_procedural_problem"

@dataclass(frozen=True)
class AuthorityHit:
    authority_id: str
    citation: str
    title: str
    court: str
    effective_from: Optional[date]
    effective_to: Optional[date]
    current_status: str
    source_url: str
    excerpt: str
    adverse: bool = False

@dataclass
class CaseFinding:
    issue: str
    status: FindingStatus
    explanation: str
    facts_used: list[str] = field(default_factory=list)
    missing_facts: list[str] = field(default_factory=list)
    supporting: list[AuthorityHit] = field(default_factory=list)
    adverse: list[AuthorityHit] = field(default_factory=list)
    counterargument: str = ""
    confidence: float = 0.0

    def why(self) -> dict:
        return {
            "issue": self.issue,
            "status": self.status.value,
            "explanation": self.explanation,
            "facts_used": self.facts_used,
            "missing_facts": self.missing_facts,
            "supporting_authority": [a.__dict__ for a in self.supporting],
            "adverse_authority": [a.__dict__ for a in self.adverse],
            "counterargument": self.counterargument,
            "confidence": self.confidence,
        }

def authority_applies(hit: AuthorityHit, event_date: date) -> bool:
    if hit.effective_from and hit.effective_from > event_date:
        return False
    if hit.effective_to and hit.effective_to < event_date:
        return False
    return hit.current_status.lower() not in {"overruled", "vacated", "withdrawn"}

def split_authority(hits: Iterable[AuthorityHit], event_date: date):
    applicable = [h for h in hits if authority_applies(h, event_date)]
    return ([h for h in applicable if not h.adverse], [h for h in applicable if h.adverse])

def red_team(finding: CaseFinding) -> dict:
    weaknesses = []
    if finding.missing_facts:
        weaknesses.append("Material facts are missing: " + ", ".join(finding.missing_facts))
    if finding.adverse:
        weaknesses.append("Adverse authority exists and must be distinguished or addressed.")
    if not finding.supporting:
        weaknesses.append("No verified supporting authority is attached yet.")
    if finding.confidence < .7:
        weaknesses.append("Confidence is below the review threshold; attorney/source verification is required.")
    return {
        "issue": finding.issue,
        "strongest_user_position": finding.explanation,
        "strongest_counterargument": finding.counterargument or "Counterargument has not yet been supplied.",
        "weaknesses": weaknesses,
        "supporting_citations": [a.citation for a in finding.supporting],
        "adverse_citations": [a.citation for a in finding.adverse],
    }
