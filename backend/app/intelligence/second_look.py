from dataclasses import dataclass

@dataclass(frozen=True)
class SecondLookInput:
    sentence_text: str
    plea_or_trial: str
    appeal_taken: bool
    habeas_taken: bool
    issues_preserved: list[str]

CHECKS = (
    ("sentencing_legality", ("illegal sentence", "maximum", "minimum", "probation", "consecutive")),
    ("merger", ("merge", "merger", "same conduct", "included offense")),
    ("plea", ("plea", "voluntary", "knowing", "boykin")),
    ("ineffective_assistance", ("ineffective", "counsel", "strickland")),
    ("new_evidence", ("new evidence", "newly discovered", "recant")),
)

def screen(data: SecondLookInput) -> list[dict]:
    hay = " ".join([data.sentence_text, data.plea_or_trial, *data.issues_preserved]).lower()
    results=[]
    for name, needles in CHECKS:
        matched=[n for n in needles if n in hay]
        results.append({
            "issue": name,
            "status": "potential_issue" if matched else "more_information_required",
            "signals": matched,
            "procedural_note": "Check preservation, deadline, exhaustion, retroactivity, and the remedy available at the present stage."
        })
    return results
