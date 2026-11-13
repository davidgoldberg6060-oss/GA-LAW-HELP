import pytest
from app import courtroom_prep as prep
from app import language as lang


def test_general_checklist_has_day_before_and_day_of():
    pack = prep.prep_for(None, language="en")
    ids = [s["id"] for s in pack["sections"]]
    assert ids[:2] == ["day_before", "day_of"]
    assert "Your Honor" in pack["quick"] or "Your Honor" in " ".join(
        i for s in pack["sections"] if s["id"] == "address_judge" for i in s["items"]
    )
    assert pack["notice"] == lang.NOTICE_EN
    assert "not legal advice" in pack["disclaimer"].lower()
    titles = {s["id"]: s["title"] for s in pack["sections"]}
    assert titles["bring"] == "What to bring" and titles["wear"] == "What to wear"
    assert titles["say"] == "What to say" and titles["dont_say"] == "What not to say"
    assert titles["arrive"] == "Arriving early"


def test_dui_checklist_is_tailored_and_keeps_general_points():
    pack = prep.prep_for("dui")
    assert pack["case_type"] == "dui" and pack["label"] == "DUI"
    text = prep.as_text(pack)
    assert "implied-consent" in text.lower() or "ALS" in text or "license" in text.lower()
    assert "Your Honor" in text
    assert "30 to 45 minutes" in text
    assert text.endswith("\n")
    assert lang.NOTICE_EN in text


def test_eviction_checklist_is_civil_and_mentions_dispossessory():
    pack = prep.prep_for("eviction")
    assert pack["family"] == "civil"
    blob = " ".join(i for s in pack["sections"] for i in s["items"])
    assert "dispossessory" in blob.lower() or "summons" in blob.lower()


def test_spanish_checklist_keeps_your_honor_and_spanish_disclaimer():
    pack = prep.prep_for("traffic", language="es")
    assert pack["language"] == "es"
    assert pack["notice"] == lang.NOTICE_ES
    assert "Your Honor" in pack["quick"] or any("Your Honor" in i for s in pack["sections"] for i in s["items"])
    assert any(s["title"] == "El día antes de la corte" for s in pack["sections"])
    assert "no asesoramiento jurídico" in pack["notice"]


def test_detects_case_type_from_a_situation():
    pack = prep.prep_for(situation="I have a court date for a DUI after a traffic stop")
    assert pack["case_type"] == "dui"


def test_unknown_type_falls_back_to_general():
    pack = prep.prep_for("not-a-real-type")
    assert pack["case_type"] is None or pack["case_type"] == ""
    assert pack["family"] == "general"
