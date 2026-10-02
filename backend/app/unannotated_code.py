"""Official unannotated Georgia code is the statute source. No annotated OCGA."""
from __future__ import annotations

UNANNOTATED_SOURCE = {
    "name": "Code of Georgia, unannotated",
    "publisher": "Georgia General Assembly / GeorgiaNet",
    "host": "https://www.legis.ga.gov/",
    "rule": "Import statute text only. Drop annotations, headnotes, and editor notes.",
}

TITLES = [
    {"title": 9, "name": "Civil Practice"},
    {"title": 15, "name": "Courts"},
    {"title": 16, "name": "Crimes and Offenses"},
    {"title": 17, "name": "Criminal Procedure"},
    {"title": 19, "name": "Domestic Relations"},
    {"title": 24, "name": "Evidence"},
    {"title": 40, "name": "Motor Vehicles and Traffic"},
]

ENCOUNTER_SECTIONS = [
    {"citation": "OCGA 17-4-20", "topic": "Arrest without a warrant"},
    {"citation": "OCGA 17-5-1", "topic": "Search incident to arrest"},
    {"citation": "OCGA 17-5-30", "topic": "Motion to suppress"},
    {"citation": "OCGA 16-10-24", "topic": "Obstruction"},
    {"citation": "OCGA 16-10-20", "topic": "False statements"},
    {"citation": "OCGA 40-5-55", "topic": "Implied consent"},
    {"citation": "OCGA 40-6-395", "topic": "Fleeing or eluding"},
]

def statute_seed() -> dict:
    return {
        "source": UNANNOTATED_SOURCE,
        "titles": TITLES,
        "encounter_sections": ENCOUNTER_SECTIONS,
        "complete": False,
    }
