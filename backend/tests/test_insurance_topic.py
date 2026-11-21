"""Nov 21 live check: "The other driver's insurance company keeps calling me ... recorded statement" was titled
"Your Civil Plan: Protective order" because "keeps calling" matched the harassment pattern."""
import pytest

from app import civil_guide as cg
from app import defense_plan as dp

INSURANCE = [
    "The other driver's insurance company keeps calling me after my car accident and wants a recorded statement. What should I do?",
    "The insurance adjuster keeps calling and pressuring me to settle my wreck",
    "Their insurance keeps calling me, do I have to give a recorded statement?",
    "My homeowners insurance denied my claim after the fire",
    "The insurer keeps harassing me to sign a release after my accident",
]
PROTECTIVE = [
    "My ex keeps calling me and threatening me, I want a protective order",
    "He keeps calling me and showing up at my job",
    "My boyfriend keeps texting me threats",
    # safety first: a person threatening wins even when an insurer is also mentioned
    "My insurance company keeps calling me and my ex keeps threatening me",
]


@pytest.mark.parametrize("q", INSURANCE)
def test_insurance_questions_get_the_insurance_topic(q):
    assert cg.detect(q)["key"] == "insurance_claim"
    assert "protective_order" not in [c["key"] for c in cg.detect_all(q)]
    plan = dp.plan_for(q)
    if plan:
        assert dp.title_line(plan) == "Your Civil Plan: Insurance claim problem"


@pytest.mark.parametrize("q", PROTECTIVE)
def test_harassment_by_a_person_still_gets_a_protective_order(q):
    assert cg.detect(q)["key"] == "protective_order"


def test_the_live_question_is_titled_insurance():
    q = INSURANCE[0]
    plan = dp.plan_for(q)
    assert plan and dp.title_line(plan) == "Your Civil Plan: Insurance claim problem"


def test_plain_car_wreck_stays_a_car_wreck():
    for q in ("I was in a car wreck in Atlanta yesterday, the other driver ran a red light. What should I do?",
              "The adjuster offered me 2000 for my car wreck injuries, should I take it?"):
        assert cg.detect(q)["key"] == "car_wreck", q
