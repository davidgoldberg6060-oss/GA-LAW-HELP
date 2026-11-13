"""'Things you may not know to ask': related problems, root causes, and hidden deadlines from the user's facts."""
import re

from app import defense_plan as dp
from app import hidden_issues as hi


def _qs(kind, facts):
    return [i["question"] for i in hi.pick(kind, facts)]


def test_dui_surfaces_als_appeal_and_implied_consent():
    qs = _qs("dui", "I got arrested for DUI in Cobb last night and they took my blood")
    assert qs[0] == "Do I have to appeal my license suspension within 30 days?"
    assert any("blood or breath test" in q for q in qs)


def test_dui_skips_als_when_user_already_appealed_and_adds_crash():
    qs = _qs("dui", "DUI after a wreck on I-75, I already appealed the license suspension with an ALS hearing")
    assert not any("30 days" in q for q in qs) and any("crash" in q for q in qs)


def test_arrest_brings_bond_probation_hold_and_immigration():
    qs = _qs("criminal", "I was arrested for battery, released on bond, and I'm on probation for something else")
    assert "What happens if I break a bond condition?" in qs and "Can this arrest cause a probation hold?" in qs
    assert len(qs) <= hi.MAX_ITEMS


def test_charge_asks_about_search_and_talking_to_police_when_not_said():
    qs = _qs("theft", "My daughter was charged with shoplifting at Walmart")
    assert any("searched" in q for q in qs) or any("told police" in q for q in qs)
    assert not any("searched" in q for q in _qs("drugs", "they searched my car and found weed"))


def test_eviction_covers_answer_deadline_notice_retaliation_condition_deposit():
    items = hi.pick("eviction", "landlord filed a dispossessory after I complained about mold and a broken heater")
    qs = [i["question"] for i in items]
    assert qs[0].startswith("Is this eviction retaliation")
    assert any("7 days" in i["why"] for i in items)
    assert len(items) == 4


def test_custody_brings_child_support_and_protective_orders():
    qs = _qs("custody", "My ex threatened me and wants to move out of state with our son")
    assert any("protective order" in q for q in qs) and any("out of state" in q for q in qs)
    assert any("child support" in q.lower() for q in _qs("custody", "I want to change custody of my daughter"))


def test_items_are_short_tappable_and_each_has_one_line_why():
    for kind in list(hi.ITEMS) + ["criminal"]:
        for i in hi.pick(kind, "I was arrested and charged, released on bond, sued, fired, on probation"):
            assert i["question"].endswith("?") and len(i["question"]) <= 80
            assert 10 < len(i["why"]) <= 140 and "\n" not in i["why"]
            assert not re.search(r"O\.C\.G\.A|§", i["question"] + i["why"])  # no citations to verify


def test_plan_gets_section_before_lawyer_questions_and_chips():
    plan = dp.plan_for("I got arrested for DUI last night and refused the breath test, build my defense")
    text = "Quick answer\nX.\n\nQuestions to ask your lawyer\n• Q?\n\nWhere to get help\n• y"
    out = dp.add_hidden_issues(plan, text)
    assert out.index(hi.HEADING) < out.index("Questions to ask your lawyer")
    assert "Why it matters:" in out
    chips = dp.follow_ups(plan)
    assert 1 <= len(chips) <= 3 and chips[0] == "Do I have to appeal my license suspension within 30 days?"
    assert all(len(c) <= 120 for c in chips)


def test_clarify_plans_keep_their_examples_and_get_no_section():
    plan = dp.plan_for("I got arrested, build my defense")
    assert plan["status"] == "clarify" and dp.hidden_issues(plan) == []
    assert dp.add_hidden_issues(plan, "Body") == "Body"
