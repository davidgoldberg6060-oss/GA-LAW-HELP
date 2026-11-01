from datetime import date
from types import SimpleNamespace

from app.case_guide import OPTIONS, build_guide, detect_stage


def _exists(missing=()):
    return lambda c: None if c in missing else SimpleNamespace(id=1, title=f"{c}. Title here")


def test_every_stage_returns_cited_options_and_never_uncited_ones():
    for stage in OPTIONS:
        g = build_guide(None, stage=stage, exists=_exists())
        assert g["options"] and all(o["citations"] for o in g["options"]) and g["next_steps"]
    g = build_guide(None, stage="record", exists=_exists({"O.C.G.A. § 35-3-37"}))
    assert all(o["key"] != "restriction" for o in g["options"])  # dropped: law not stored


def test_prison_deadlines_and_issue_highlighting():
    g = build_guide(None, stage="prison", details={"sentence_date": "2026-03-01", "issues": "my lawyer never investigated"},
                    today=date(2026, 11, 1), exists=_exists())
    assert g["options"][0]["key"] == "habeas"  # bad lawyer -> habeas first
    mod = next(o for o in g["options"] if o["key"] == "sentence_mod")
    assert mod["deadline_status"]["days_left"] == 120 and not mod["deadline_status"]["passed"]
    assert [t["title"] for t in g["timeline"]][0].startswith("Sentence reduction")
    s = build_guide(None, stage="sentenced", details={"sentence_date": "2026-09-01"}, today=date(2026, 11, 1), exists=_exists())
    assert next(o for o in s["options"] if o["key"] == "mnt")["deadline_status"]["passed"]


def test_detect_stage():
    assert detect_stage("I'm in prison and want to get out early") == "prison"
    assert detect_stage("they offered me a plea deal") == "plea"
    assert detect_stage("my PO said I violated") == "probation"
    assert detect_stage("how do I expunge an old arrest") == "record"
    assert detect_stage("got arrested last night, what about bond") == "arrested"
    assert detect_stage("what's the weather") is None


def test_neutral_wording_and_family_tips():
    import re
    for stage in OPTIONS:
        g = build_guide(None, stage=stage, exists=_exists())
        text = " ".join(g["next_steps"] + [o["what"] + " " + o["title"] + " " + (o["where"] or "") for o in g["options"]])
        assert not re.search(r"\b(you|your|I|my)\b", text), (stage, text)
    g = build_guide(None, stage="arrested", exists=_exists())
    assert any("bond" in t for t in g["family_tips"]) and any("books" in t for t in g["family_tips"])
