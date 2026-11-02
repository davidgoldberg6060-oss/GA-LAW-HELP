from datetime import date
from types import SimpleNamespace
from app import case_guide
from app.grounded_legal_assistant import SICK_CALL_STEP, _PRACTICAL

def _ex(c): return SimpleNamespace(id=1, title=c)

def test_prison_stage_is_neutral_and_has_find_case():
    assert dict(case_guide.STAGES)["prison"].startswith("Serving a sentence")
    g = case_guide.build_guide(None, stage="prison", details={"situation": "my son has been locked up 5 years"}, today=date(2026, 11, 1), exists=_ex)
    blob = str(g).lower()
    for bad in ("you are in prison", "your cell", "file a grievance yourself"):
        assert bad not in blob
    assert any("offender" in r["title"].lower() for r in g["find_case"])
    assert "on their behalf (9-14-44)" in str(g["options"])

def test_detects_loved_one_custody():
    assert case_guide.detect_stage("my brother is locked up serving his sentence") == "prison"

def test_conditions_wording_is_outside_helper():
    assert "warden" in SICK_CALL_STEP and "Ombudsman" in SICK_CALL_STEP
    assert "family or a friend on the outside" in _PRACTICAL
