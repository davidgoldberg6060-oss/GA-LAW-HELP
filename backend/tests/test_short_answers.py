"""Shorter, phone-friendly answers: prompt asks for short bullets at an ~8th-grade level, motions are one line each,
and a 'searched without a warrant' question doesn't get arrest-warrant follow-ups."""
from app import defense_help as dh
from app.civil_topics import follow_ups
from app.grounded_legal_assistant import _mode_instructions

CAR = "I was charged with possession after police searched my car without a warrant"


def test_prompt_asks_for_short_plain_bullets_and_defense_groups():
    p = _mode_instructions("general", CAR)
    assert "8th-grade" in p and "at most 4 bullets" in p and "1-3 short sentences" in p
    assert "'Ways to fight the evidence:'" in p and "'Ways to lessen the outcome:'" in p
    assert "Questions to ask your lawyer" in p and "Motions that could help" in p


def test_motion_lines_are_short_and_keep_how_it_helps_and_timing():
    m = {"title": "Motion to suppress evidence", "citations": ["O.C.G.A. § 17-5-30"], "purpose": "Asks the judge to throw out evidence.",
         "when_it_applies": "May apply if a search had no warrant, consent, or legal reason.", "how_it_helps": "Charges may be dropped.",
         "timing": "Within ten days after arraignment.", "draftable": False}
    line = dh.motions_section([m], False).splitlines()[1]
    assert line == "• Motion to suppress evidence (O.C.G.A. § 17-5-30): Asks the judge to throw out evidence. How it can help: Charges may be dropped. Timing: Within ten days after arraignment."
    assert len(dh.motion_keys(CAR)) <= dh.MAX_MOTIONS == 4


def test_warrantless_search_question_gets_defense_follow_ups():
    assert follow_ups(CAR) == list(dh.CHARGE_FOLLOW_UPS)
    assert follow_ups("is there a warrant out for me")[0] == "How can I check if there is a warrant?"
    assert len(follow_ups(CAR)) <= 3
