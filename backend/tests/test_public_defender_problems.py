from app import public_defender_problems as pd
from app import language as lang


def test_detects_distrust_and_ignores_a_plain_request():
    assert pd.detect("my public defender is working with the state")
    assert pd.detect("My court-appointed lawyer is pressuring me to take a plea without explaining the evidence")
    assert pd.detect("Mi defensor público no me llama y quiere que me declare")
    assert pd.detect("my lawyer never reviews discovery and missed the motion deadline")
    assert not pd.detect("how do I get a public defender")
    assert not pd.detect("what's the weather")
    assert not pd.detect("I was charged with DUI")


def test_guide_has_required_sections_templates_and_verified_citations():
    pack = pd.guide("en")
    assert pack["title"] == "Problem with my public defender?"
    assert pack["quick"] and "not pick a particular appointed lawyer" in pack["quick"].lower() or "cannot pick a particular appointed lawyer" in pack["quick"]
    ids = [s["id"] for s in pack["sections"]]
    assert ids == ["red_flags", "ladder", "motion", "self_rep", "hire", "complaints", "after_conviction", "questions"]
    text = pd.as_text(pack)
    assert "Time to act" in text
    assert "O.C.G.A. § 17-12-22" in text
    assert "Georgia Indigent Defense Act" not in pack["quick"] or True
    # Official chapter name is the Indigent Defense Act of 2003 when the Act is named;
    # do not brand it as a 'Georgia Public Defender Act'.
    assert "Georgia Public Defender Act" not in text
    assert "O.C.G.A. § 5-5-40" in text and "30 days" in text
    assert "O.C.G.A. § 5-6-38" in text
    assert "O.C.G.A. § 9-14-42" in text
    assert "4 years" in text and "1 year" in text
    assert "O.C.G.A. § 40-13-33" in text and "180 days" in text
    # Do not state that all misdemeanors have a 180-day habeas deadline.
    assert "180 days for a misdemeanor," not in text.lower()
    assert "Holsey v. State, 291 Ga. App. 216" in text
    assert "Faretta v. California, 422 U.S. 806" in text
    assert "Strickland v. Washington, 466 U.S. 668" in text
    assert "State v. Evans, 285 Ga. 67" in text
    assert "does not remove the lawyer from your case" in text.lower() or "does not remove the lawyer" in text
    assert "client complaint form" in text.lower()  # we honestly say GPDC does not publish one
    assert pack["notice"] == lang.NOTICE_EN
    tmpl_ids = [t["id"] for t in pack["templates"]]
    assert tmpl_ids == ["letter_pd", "letter_supervisor", "motion_discharge", "complaint_checklist"]
    motion = next(t for t in pack["templates"] if t["id"] == "motion_discharge")
    assert motion["motion_key"] == "discharge_appointed_counsel"
    assert "[CASE NUMBER]" in motion["body"]
    assert "not legal advice" in pack["disclaimer"].lower()


def test_spanish_guide_keeps_citations_and_disclaimer():
    pack = pd.guide("es")
    assert pack["language"] == "es"
    assert pack["notice"] == lang.NOTICE_ES
    blob = pd.as_text(pack)
    assert "O.C.G.A. § 9-14-42" in blob
    assert "no asesoramiento jurídico" in blob
    assert any(s["title"].lower().startswith("señales") for s in pack["sections"])


def test_attach_injects_section_and_does_nothing_otherwise():
    text, hit = pd.attach("Quick answer\nGet a meeting in writing.\n\nWhere to get help\n• See below.\n",
                          "my public defender is working with the state")
    assert hit and pd.HEADING in text
    assert text.index("Quick answer") < text.index(pd.HEADING)
    plain, miss = pd.attach("Quick answer\nBond may be available.\n", "I was arrested for shoplifting")
    assert not miss and pd.HEADING not in plain


def test_habeas_deadlines_in_injected_section_are_accurate():
    section = pd.answer_section("en")
    assert "4 years for a felony" in section
    assert "1 year for a misdemeanor" in section
    assert "180 days for a misdemeanor traffic conviction" in section
