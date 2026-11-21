"""Every civil problem gets civil help: divorce, car wrecks, falls, work injuries, insurance denials, fire damage,
landlord, debt, wills, name changes, protective orders ... and a catch-all for anything not listed.

Law text in ``civil_sections_fixture.json`` is copied from the stored 2022 Code text in the law database."""
import contextlib
import json
import pathlib
import re

import pytest

from app import civil_guide as cg
from app import defense_plan as dp
from app import grounded_legal_assistant as service
from app import help_resources as hr
from app.civil_check_service import GUIDE_ONLY, analyze_civil_check, civil_check_note_text
from app.civil_topics import topic_sections
from app.slang import plain_terms

LAW = json.loads((pathlib.Path(__file__).with_name("civil_sections_fixture.json")).read_text())


def hit(sec):
    row = LAW.get(sec) or {"title": sec, "text": f"Text of {sec}."}
    return {"corpus": "persisted_authorities", "title": row["title"], "citation": f"O.C.G.A. § {sec}",
            "source_url": "https://archive.org/download/gov.ga.ocga.2018/release86.2022", "verification_status": "verified",
            "excerpt": row["text"][:1800], "full_text": row["text"], "record_type": "statute"}


class FakeDB:
    @contextlib.contextmanager
    def begin_nested(self):
        yield


@pytest.fixture
def wired(monkeypatch):
    import app.charge_check_service as ccs
    monkeypatch.setattr(service, "_hybrid_retrieval", lambda q, m, db, l: {"hits": []})
    monkeypatch.setattr(ccs, "lookup_sections", lambda db, secs: [hit(s) for s in secs])
    monkeypatch.setattr(service, "exact_citation_results", lambda db, cites: [])


CASES = [
    ("My wife and I want a divorce in Gwinnett County. We have two kids and a house.", "divorce", "divorce"),
    ("My ex stopped paying child support 4 months ago. What can I do?", "custody", "custody"),
    ("I was rear-ended at a red light in Atlanta and hurt my neck. Their insurance offered $1,500.", "car_wreck", "car_wreck"),
    ("I slipped on a wet floor at a grocery store and broke my wrist. There was no sign.", "slip_and_fall", "slip_and_fall"),
    ("I fell off a ladder at work and hurt my back. My boss says don't file anything.", "workers_comp", "workers_comp"),
    ("My homeowners insurance denied my claim for water damage from a burst pipe.", "insurance_claim", "insurance_claim"),
    ("My house caught fire from a neighbor's yard fire and has smoke damage.", "property_damage", "property_damage"),
    ("My landlord put a notice on my door saying I have to leave in 3 days because I'm behind on rent.", "landlord_tenant", "eviction"),
    ("A debt collector is garnishing my paycheck for an old credit card.", "debt", "debt"),
    ("My employer didn't pay me for my last two weeks and fired me for complaining about overtime.", "employment", "employment"),
    ("The hospital left a sponge inside me after surgery and I needed a second surgery.", "medical_malpractice", "medical_malpractice"),
    ("My neighbor's dog bit my son on the leg and he needed stitches.", "dog_bite", "dog_bite"),
    ("I paid a contractor $8,000 to redo my kitchen and he quit halfway.", "contract", "contract"),
    ("My father died without a will and my sister is living in his house.", "probate", "probate"),
    ("A used car dealer lied to me about the car never being in a flood.", "consumer", "consumer"),
    ("I'm 3 months behind on my mortgage and got a foreclosure letter.", "foreclosure", "foreclosure"),
    ("I want to legally change my name in Georgia.", "name_change", "name_change"),
    ("My ex-boyfriend keeps threatening me and showing up at my job.", "protective_order", "protective_order"),
    ("My HOA is fining me $50 a day for my mailbox color.", "hoa_neighbor", "hoa_neighbor"),
    ("Someone opened credit cards in my name and now collectors are calling me.", "identity_theft", "identity_theft"),
]


@pytest.mark.parametrize("text,cat,plan_key", CASES)
def test_every_civil_problem_gets_a_civil_plan(text, cat, plan_key):
    assert cg.detect(text)["key"] == cat
    p = dp.plan_for(text)
    assert p and p["status"] == "build" and p["case_type"] == plan_key and p["family"] == "civil", p
    secs = dp.plan_sections(p)
    assert secs and not any(s.startswith(("17-", "16-13", "40-6-181", "42-8")) for s in secs), secs


@pytest.mark.parametrize("text,kind", [
    ("I was charged with stalking my ex", "criminal"),
    ("I got a ticket for running a red light and hit another car", "traffic"),
    ("I was arrested for DUI after a car accident", "dui"),
    ("My son got caught shoplifting at Walmart, first offense", "theft"),
])
def test_accused_person_still_gets_the_criminal_plan(text, kind):
    p = dp.plan_for(text)
    assert p["case_type"] == kind and p["family"] == "criminal"


def test_info_questions_keep_the_normal_answer_but_get_civil_help():
    q = "Can I get workers comp if I got hurt at work?"
    assert dp.plan_for(q) is None
    assert cg.detect(q)["key"] == "workers_comp"
    assert [r["id"] for r in hr.route(q)][0] == "sbwc"
    assert hr.lawyer_questions(q) == list(cg.get("workers_comp")["questions"])


@pytest.mark.parametrize("text,agency", [
    ("I fell off a ladder at work and hurt my back", "sbwc"),
    ("My homeowners insurance denied my claim", "insurance_commissioner"),
    ("I was rear-ended and the other driver's insurance offered $1,500", "insurance_commissioner"),
    ("The surgeon left a sponge inside me", "medical_board"),
    ("My ex stopped paying child support", "child_support_services"),
    ("I got a foreclosure letter on my house", "housing_counselor"),
    ("Someone opened credit cards in my name", "identity_theft_gov"),
    ("My employer never paid me my overtime", "wage_hour"),
    ("My father died and we need to probate his will", "probate_courts"),
    ("My ex keeps threatening me, I need a protective order", "dv_hotline"),
])
def test_help_routes_to_the_right_agency_and_legal_aid(text, agency):
    ids = [r["id"] for r in hr.route(text)]
    assert agency in ids and ("glsp" in ids or "atlanta_legal_aid" in ids), ids
    assert "public_defender" not in ids  # victims and claimants are not facing charges
    for r in hr.route(text):
        assert r["url"].startswith("https://")


def test_catalog_is_well_formed():
    for c in cg.CATEGORIES + (cg.OTHER,):
        assert c["steps"] and c["questions"] and c["label"]
        assert all(q.endswith("?") for q in c["questions"])
        assert all(h in hr.R for h in c["help"]), c["key"]
        assert set(c["deadlines"]) <= set(c["sections"]) | set(c["deadlines"])
        for s in c["steps"] + c["questions"]:
            # no invented legal numbers in the curated text
            assert not re.search(r"\b\d+\s*(days?|months?|years?)\b|\$\s?\d", s), (c["key"], s)


def test_deadline_quote_is_word_for_word_from_the_law_text():
    q = cg.deadline_quote(LAW["9-3-33"]["text"])
    assert q and q in LAW["9-3-33"]["text"] and "two years" in q
    q = cg.deadline_quote(LAW["34-9-82"]["text"])
    assert q and q in LAW["34-9-82"]["text"] and "one year" in q
    assert cg.deadline_quote("Contract defined. A contract is an agreement.") is None


def test_slang_and_topic_regressions():
    assert "arrest" not in plain_terms("My house caught fire last night")
    assert "arrest" in plain_terms("I got caught with weed")
    assert not set(topic_sections("I got fired from my job")) & {"51-1-6", "44-7-14"}
    assert not set(topic_sections("what will happen to my car")) & {"53-4-20"}


CAR = "I was rear-ended at a red light in Atlanta 3 weeks ago and hurt my neck. The other driver's insurance is offering $1,500."
CAR_MODEL = ("Quick answer\nYou may have an injury claim. Don't accept the first offer yet.\n\n"
             "What you'd need to show\n- Likely claim: negligence (O.C.G.A. § 51-1-6).\n- Fault: you were stopped at a light.\n\n"
             "What the other side may say\n- Your injury is minor.\n\nYour rights\n- To medical care.\n\n"
             "Key deadlines\n- Ask a lawyer soon; Georgia has time limits for filing.\n\n"
             "Evidence to gather now\n- Medical records.\n\nQuestions to ask your lawyer\n- What is my claim worth?\n\nWhere to get help\n- x")


def test_car_wreck_plan_is_civil_with_steps_and_verified_deadline(wired):
    prompts = []
    r = service.grounded_legal_response(CAR, "general", lambda p: prompts.append(p) or CAR_MODEL, db=FakeDB())
    p = prompts[0]
    assert "AUTOMATIC CIVIL PLAN (Car wreck injury)" in p and "What you'd need to show" in p and "not a criminal case" in p.lower()
    assert "O.C.G.A. § 9-3-33" in p and "O.C.G.A. § 51-1-6" in p and "17-5-30" not in p
    a = r["analysis"]
    assert a.startswith("Your Defense Plan: Car wreck injury\n")
    assert "Steps to take now" in a and "police accident report" in a
    assert '"Except as otherwise provided in this article, actions for injuries to the person shall be brought within two years' in a
    assert r["suggested_motions"] == [] and "Motions that could help" not in a and "suppress" not in a.lower()
    assert r["citation_check"] == "passed" and "Traffic" not in r["defense_plan"]["label"]
    assert any("9-3-33" in (x.get("citation_raw") or x.get("citation")) for x in r["authorities"])
    ids = [h["id"] for h in r["help_resources"]]
    assert "insurance_commissioner" in ids and "public_defender" not in ids
    assert r["follow_ups"] and not any("ticket" in f.lower() for f in r["follow_ups"])
    assert a.rstrip().splitlines()[-1].startswith("Note: This is legal information, not legal advice.")


def test_civil_info_question_gets_civil_instructions_and_no_criminal_motions(wired):
    prompts = []
    model = ("Short answer\nYes, most work injuries are covered.\n\nHow it works in Georgia\n- O.C.G.A. § 34-9-1 defines injury.\n\n"
             "Questions to ask your lawyer\n- Is my injury covered?\n\nDeadlines and costs\n- Ask soon.\n\nWhere to get help\n- x")
    r = service.grounded_legal_response("Can I get workers comp if I got hurt at work?", "general", lambda p: prompts.append(p) or model, db=FakeDB())
    assert "CIVIL QUESTION (Work injury (workers' comp))" in prompts[0]
    assert r["suggested_motions"] == [] and "defense_plan" not in r
    assert "34-9-82" in r["analysis"] or "34-9-80" in r["analysis"]  # verified deadline quote added
    assert r["help_resources"][0]["id"] == "sbwc"


def test_civil_check_still_helps_when_the_model_returns_nothing():
    calls = []
    r = analyze_civil_check("My ex-boyfriend keeps threatening me and showing up at my job.",
                            lambda p: calls.append(p) or "not json", lookup=lambda secs: [hit(s) for s in secs])
    assert len(calls) == 1  # a listed problem skips the section-proposal call (faster, inside the app's time limit)
    assert r["category"] == {"key": "protective_order", "label": "Protective order"}
    assert r["steps"] and r["lawyer_questions"] and r["message"] == GUIDE_ONLY
    assert r["help_resources"][0]["title"].startswith("Georgia 24-Hour Domestic Violence Hotline")
    assert all(h["url"].startswith("https://") for h in r["help_resources"])
    text = civil_check_note_text(r)
    assert "STEPS TO TAKE NOW" in text and "QUESTIONS TO ASK A LAWYER" in text


def test_civil_check_adds_verified_deadlines_without_duplicates():
    data = {"claims": [{"side": "you", "claim": "Workers' compensation", "citation": "O.C.G.A. § 34-9-1", "why": "Hurt at work."}],
            "deadlines": [{"title": "File a claim", "quote": LAW["34-9-82"]["text"][:120], "citation": "O.C.G.A. § 34-9-82"}]}
    r = analyze_civil_check("I fell off a ladder at work and hurt my back.", lambda p: json.dumps(data), lookup=lambda secs: [hit(s) for s in secs])
    cites = [d["citation"]["citation"] for d in r["deadlines"]]
    assert cites.count("O.C.G.A. § 34-9-82") == 1 and "O.C.G.A. § 34-9-80" in cites
    for d in r["deadlines"]:
        sec = re.search(r"\d+-\d+-[\d.]+", d["citation"]["citation"]).group(0)
        assert d["quote"] in LAW[sec]["text"]
    assert r["claims"] and r["message"] is None and r["help_resources"][0]["id"] == "sbwc"


def test_unlisted_civil_problem_gets_the_catch_all():
    r = analyze_civil_check("The city keeps fining me for where I park my trailer and I want to fight the fines.",
                            lambda p: "{}", lookup=lambda secs: [hit(s) for s in secs])
    assert r["category"]["key"] == "other_civil" and r["steps"] and r["lawyer_questions"] and r["help_resources"]
    assert r["message"]
