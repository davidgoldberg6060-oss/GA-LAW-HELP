from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AnalysisKind(str, Enum):
    AFFIRMATIVE_INNOCENCE = "affirmative_innocence"
    REASONABLE_DOUBT = "reasonable_doubt_or_insufficiency"
    CONSTITUTIONAL = "constitutional_or_evidence_issue"
    POST_CONVICTION = "post_conviction_or_new_evidence"


@dataclass(frozen=True)
class CaseNarrative:
    narrative: str
    charges: list[str] = field(default_factory=list)
    stage: str = "unknown"
    event_date: Optional[str] = None
    county: Optional[str] = None
    user_claims_innocence: Optional[bool] = None


@dataclass(frozen=True)
class IssueSignal:
    issue: str
    kind: AnalysisKind
    matched_signals: list[str]
    questions_to_ask: list[str]
    possible_avenues: list[str]
    note: str


# These are issue-spotting signals, not legal conclusions. Any case/statute citation
# presented to a user must come from the verified authority pipeline.
ISSUE_PATTERNS = (
    (
        "alibi_or_impossibility",
        AnalysisKind.AFFIRMATIVE_INNOCENCE,
        ("alibi", "somewhere else", "wasn't there", "was not there", "couldn't have", "could not have"),
        ("Where was the accused at the relevant time?", "What independent records or witnesses can verify that location?"),
        ("investigate alibi evidence", "preserve location/video/transaction records", "compare timeline against prosecution evidence"),
    ),
    (
        "mistaken_identification",
        AnalysisKind.AFFIRMATIVE_INNOCENCE,
        ("wrong person", "mistaken identity", "lineup", "photo array", "identified me", "eyewitness"),
        ("How was the identification conducted?", "Was the witness previously unable to identify the accused?", "What were lighting, distance, duration, and stress conditions?"),
        ("challenge identification reliability", "investigate suppression issue", "obtain lineup/photo-array records"),
    ),
    (
        "alternative_perpetrator",
        AnalysisKind.AFFIRMATIVE_INNOCENCE,
        ("someone else", "another suspect", "other suspect", "alternative suspect"),
        ("What admissible evidence connects another person to the offense?", "Did investigators document or eliminate other suspects?"),
        ("investigate alternative-perpetrator evidence", "request investigative records and physical evidence"),
    ),
    (
        "recantation_or_false_testimony",
        AnalysisKind.POST_CONVICTION,
        ("recant", "lied", "false testimony", "made it up", "changed story"),
        ("What exactly changed and when?", "Is the change documented under oath or otherwise corroborated?", "Was the original testimony material to conviction?"),
        ("investigate newly discovered evidence", "preserve recantation evidence", "evaluate post-conviction remedy"),
    ),
    (
        "forensic_or_physical_evidence_conflict",
        AnalysisKind.AFFIRMATIVE_INNOCENCE,
        ("dna", "fingerprint", "forensic", "ballistic", "video", "camera", "physical evidence"),
        ("Does the evidence exclude, contradict, or merely fail to include the accused?", "Was testing complete and was chain of custody documented?"),
        ("independent evidence review", "evaluate retesting", "compare expert conclusions with underlying data"),
    ),
    (
        "withheld_or_impeachment_evidence",
        AnalysisKind.CONSTITUTIONAL,
        ("brady", "giglio", "withheld", "not disclosed", "deal with witness", "witness deal"),
        ("What information was allegedly withheld?", "When was it discovered?", "How could it affect guilt, punishment, or witness credibility?"),
        ("evaluate disclosure violation", "seek underlying prosecution/police records", "evaluate appropriate motion or post-conviction claim"),
    ),
    (
        "unreliable_or_coerced_statement",
        AnalysisKind.CONSTITUTIONAL,
        ("coerced", "forced confession", "forced statement", "miranda", "interrogation", "confession"),
        ("Was the person in custody and interrogated?", "What warnings were given?", "Was there coercion, intoxication, impairment, or a request for counsel?"),
        ("evaluate statement suppression", "obtain full interrogation recording", "compare statement with independently known facts"),
    ),
    (
        "search_or_seizure",
        AnalysisKind.CONSTITUTIONAL,
        ("illegal search", "search warrant", "searched", "warrant", "traffic stop"),
        ("What was searched or seized?", "Was there a warrant, consent, or asserted exception?", "What evidence resulted from the search?"),
        ("evaluate suppression issue", "obtain warrant/affidavit/body-camera records"),
    ),
    (
        "insufficiency_or_missing_link",
        AnalysisKind.REASONABLE_DOUBT,
        ("no evidence", "not enough evidence", "insufficient", "only evidence", "no proof"),
        ("What evidence supports each statutory element?", "Which element does the user believe the prosecution cannot prove?"),
        ("element-by-element sufficiency analysis", "identify missing evidentiary links"),
    ),
)


def analyze_narrative(case: CaseNarrative) -> list[IssueSignal]:
    """Issue-spot a user's narrative without declaring guilt or innocence.

    Affirmative innocence is intentionally kept separate from reasonable doubt or
    insufficiency. Results identify investigation/legal research avenues only;
    authority must be verified before a citation is attached.
    """
    haystack = " ".join([case.narrative, *case.charges]).lower()
    findings: list[IssueSignal] = []

    for issue, kind, needles, questions, avenues in ISSUE_PATTERNS:
        matched = [needle for needle in needles if needle in haystack]
        if not matched:
            continue
        findings.append(
            IssueSignal(
                issue=issue,
                kind=kind,
                matched_signals=matched,
                questions_to_ask=list(questions),
                possible_avenues=list(avenues),
                note=(
                    "Potential issue only. Do not state that the person is innocent, "
                    "that evidence is exculpatory, or that a motion will succeed until "
                    "the underlying facts and controlling/current authority are verified."
                ),
            )
        )

    return findings


def next_questions(case: CaseNarrative, findings: list[IssueSignal]) -> list[str]:
    questions: list[str] = []
    if not case.charges:
        questions.append("What are the exact charges and counts?")
    if case.stage == "unknown":
        questions.append("What stage is the case at: investigation, pretrial, trial, appeal, habeas, or another post-conviction stage?")
    if not case.event_date:
        questions.append("What is the offense/event date?")
    if not case.county:
        questions.append("What Georgia county and court are involved?")
    questions.extend(q for finding in findings for q in finding.questions_to_ask)
    # Preserve order while avoiding repetitive interviewing.
    return list(dict.fromkeys(questions))
