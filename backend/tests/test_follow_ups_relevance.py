"""Suggested follow-ups must match the current question's topic and never assume custody."""
import pytest
from app.civil_topics import current_question, follow_ups

ANDROID = ("Continue a focused STANDALONE ASSISTANT legal-information conversation. Stay within Georgia law, rights, "
           "police encounters, criminal/civil legal procedure, motions, sentencing, incarceration/post-conviction issues, appeals.\n"
           "Conversation so far (recent context only):\nUser: earlier question\nSTANDALONE ASSISTANT: earlier answer\n\nUser: ")
SELF_DEFENSE_ANSWER = "O.C.G.A. 16-3-21 justification; 16-3-24.2 immunity from prosecution. Prison penalties may apply if convicted."
JAILISH = ("prison", "jail", "incarcerat", "custody", "corrections", "grievance")


def _jailish(items):
    return any(w in s.lower() for s in items for w in JAILISH)


def test_current_question_strips_app_preamble_and_history():
    assert current_question(ANDROID + "Is speeding a crime?") == "Is speeding a crime?"
    assert current_question("plain question") == "plain question"


@pytest.mark.parametrize("q,expect", [
    ("Can I claim self defense if someone attacked me first?", "self-defense"),
    ("My landlord filed a dispossessory against me", "dispossessory"),
    ("I got a speeding ticket in Cobb", "traffic ticket"),
    ("I was arrested for DUI", "ALS hearing"),
    ("How do I appeal a conviction?", "notice of appeal"),
    ("How do I get custody of my kids?", "custody"),
    ("Can you explain this court document?", "document"),
    ("Can I get my record restricted?", "restricted"),
    ("A collector is garnishing my wages", "garnishment"),
])
def test_topic_specific_and_no_assumed_incarceration(q, expect):
    for text in (q, ANDROID + q):
        out = follow_ups(text, SELF_DEFENSE_ANSWER)
        assert out and any(expect.lower() in s.lower() for s in out), out
        if "custody of my kids" not in q:
            assert not _jailish(out), out


def test_explicit_jail_conditions_still_get_jail_follow_ups():
    out = follow_ups(ANDROID + "My brother is in jail and they won't give him medical care")
    assert any("grievance" in s.lower() for s in out)


def test_answer_words_alone_never_trigger_jail_follow_ups():
    assert not _jailish(follow_ups(ANDROID + "What is the law here?", "inmates in prison may file a grievance"))


def test_unrelated_question_gets_no_generic_filler():
    assert follow_ups(ANDROID + "What is the capital of France?", "I can only help with Georgia law.") == []


def test_public_endpoint_uses_current_question(monkeypatch):
    from app import main
    r = main._decorate_public({"answer": SELF_DEFENSE_ANSWER}, ANDROID + "Can I claim self defense?", "talk_to_me")
    assert r["follow_ups"] and not _jailish(r["follow_ups"])
    assert r.get("case_stage") != "prison"
