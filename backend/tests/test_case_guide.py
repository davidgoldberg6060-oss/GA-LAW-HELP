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


def _g(stage, situation, answers=None, **dates):
    return build_guide(None, stage=stage, details={"situation": situation, **dates}, today=date(2026, 11, 1), exists=_exists(), answers=answers)


def test_scenario_drug_possession_warrantless_search():
    g = _g("pretrial", "charged with possession of cocaine after police searched my car without a warrant, first offense", arraignment_date="2026-10-28")
    keys = [m["key"] for m in g["motions"]]
    assert keys[0] == "suppress" and "conditional_discharge" in keys[:3]
    assert next(m for m in g["motions"] if m["key"] == "suppress")["deadline_status"]["days_left"] == 6


def test_scenario_asks_follow_up_when_search_facts_missing():
    g = _g("pretrial", "charged with possession, they found weed in the car")
    assert any(q["id"] == "search_warrant" for q in g["questions"])
    g2 = _g("pretrial", "charged with possession, they found weed in the car", answers={"search_warrant": "no"})
    assert g2["motions"][0]["key"] == "suppress" and not any(q["id"] == "search_warrant" for q in g2["questions"])


def test_scenario_fight_self_defense_battery():
    g = _g("pretrial", "got jumped and defended myself, now charged with battery")
    assert g["motions"][0]["key"] == "immunity"


def test_scenario_sentenced_shoplifting_within_one_year():
    g = _g("sentenced", "sentenced for felony shoplifting, 3 years, spent 60 days in jail before sentencing", sentence_date="2026-05-01")
    mod = next(m for m in g["motions"] if m["key"] == "sentence_mod")
    assert not mod["deadline_status"]["passed"] and "time_credit" in [m["key"] for m in g["motions"]]


def test_scenario_prison_five_years_lawyer_never_filed_appeal():
    g = _g("prison", "convicted at trial in 2021, been in prison 5 years, my lawyer never filed the appeal I asked for", sentence_date="2021-10-01")
    assert g["motions"][0]["key"] == "habeas"
    assert next(m for m in g["motions"] if m["key"] == "sentence_mod")["deadline_status"]["passed"]


def test_scenario_self_defense_murder():
    t = "charged with murder and felony murder, he attacked me with a knife and I shot him defending myself; I talked to police without a lawyer"
    pre = _g("pretrial", t)
    keys = [m["key"] for m in pre["motions"]]
    for k in ("immunity", "suppress_statements", "lesser_offenses", "bond_reduction", "speedy_trial"):
        assert k in keys, k
    assert keys.index("immunity") < 3
    cites = {c["citation"] for m in pre["motions"] for c in m["citations"]}
    for s in ("16-3-24.2", "16-3-20", "16-3-21", "16-3-23", "16-3-23.1", "16-5-2", "16-5-3", "17-6-1", "24-8-824", "17-7-171"):
        assert f"O.C.G.A. § {s}" in cites, s
    trial = _g("trial", t)
    assert "jury_charge_justification" in [m["key"] for m in trial["motions"]][:3]
    post = _g("prison", "convicted of murder after trial, claimed self-defense, lawyer never investigated", sentence_date="2024-01-01")
    assert {"habeas", "sentence_mod"} <= {m["key"] for m in post["motions"]}


def test_draft_is_template_with_caption_signature_and_only_code_cites():
    from app.motions import draft, TEMPLATE_BANNER
    d = draft("suppress", {"defendant": "John Doe", "county": "Fulton", "charge": "Possession of cocaine", "situation": "Car searched without a warrant."},
              lambda c: {"citation": c, "title": "Title", "id": 1})
    t = d["text"]
    assert t.startswith(TEMPLATE_BANNER) and "FULTON COUNTY" in t and "STATE OF GEORGIA" in t and "John Doe" in t
    assert "CERTIFICATE OF SERVICE" in t and "O.C.G.A. § 17-5-30" in t and " v. State" not in t and "Ga. App." not in t
    import pytest
    with pytest.raises(ValueError):
        draft("speedy_trial", {}, lambda c: None)
