"""Automatic "Your Defense Plan": built for a user's own situation (typed or uploaded), clarifying questions when
too vague, element-by-element case against / how to fight back, verified citations only, motion-maker links."""
import contextlib
import re

import pytest

from app import answer_cache
from app import defense_plan as dp
from app import grounded_legal_assistant as service

TITLES = {"40-6-391": "Driving under the influence", "40-6-392": "Chemical tests for alcohol or drugs", "40-5-67.1": "Chemical tests",
          "40-5-67": "Seizure and disposition of driver's license", "17-5-30": "Motion to suppress evidence illegally seized generally",
          "24-8-824": "Only voluntary confessions admissible", "17-16-4": "Disclosure required by prosecuting attorney and defendant",
          "17-7-170": "Demand for speedy trial", "42-8-60": "Probation prior to adjudication of guilt", "16-13-30": "Possession of controlled substances",
          "16-13-2": "Conditional discharge", "16-8-14": "Theft by shoplifting", "16-8-2": "Theft by taking", "44-7-50": "Demand for possession",
          "44-7-51": "Issuance of summons", "44-7-52": "When tender of payment by tenant serves as complete defense", "44-7-53": "When writ of possession issued",
          "44-7-54": "Payment of rent into court", "44-7-55": "Judgment", "44-7-56": "Appeal", "19-9-3": "Child custody", "19-9-23": "Change of custody",
          "42-8-34.1": "Revocation of probated sentence", "42-8-38": "Arrest or graduated sanctions for probationers", "40-6-181": "Maximum limits",
          "40-13-3": "Traffic offenses triable on complaint", "17-3-1": "Generally", "17-6-1": "When offenses bailable"}


def hit(sec):
    return {"corpus": "persisted_authorities", "title": TITLES.get(sec, sec), "citation": f"O.C.G.A. § {sec}",
            "source_url": "https://archive.org/download/gov.ga.ocga.2018/release86.2022", "verification_status": "verified",
            "excerpt": f"Text of {sec}.", "record_type": "statute"}


class FakeDB:
    @contextlib.contextmanager
    def begin_nested(self):
        yield


@pytest.fixture
def wired(monkeypatch):
    import app.charge_check_service as ccs
    monkeypatch.setattr(service, "_hybrid_retrieval", lambda q, m, db, l: {"hits": []})
    monkeypatch.setattr(ccs, "lookup_sections", lambda db, secs: [hit(s) for s in secs if s in TITLES])
    monkeypatch.setattr(service, "exact_citation_results", lambda db, cites: [])
    return []


DUI_MODEL = ("Quick answer\nYour strongest angle is the blood test. Ask for the ALS hearing right away.\n\n"
             "How they'd build the case against you\n- Likely charge: DUI under O.C.G.A. § 40-6-391.\n"
             "- Driving: They'd point to the stop and bodycam. They'd still need proof you were driving.\n"
             "- Impairment: They'd point to the blood test. They'd still need a reliable lab result.\n- Weak spots: who drew the blood is unknown.\n\n"
             "How to fight back\n- Impairment: The State cannot establish impairment because the sample's handling is unproven. Challenge: chain of custody. Motion: Motion to suppress evidence.\n\n"
             "Ways to challenge the evidence\n- Illegal stop: ask what the officer saw.\n\nYour rights\n- A lawyer or public defender.\n\n"
             "Options to lessen the outcome\n- First Offender (O.C.G.A. § 42-8-60) may apply if you have no felony.\n\n"
             "Key deadlines\n- Check your paperwork for the license deadline.\n\nEvidence to gather now\n- Hospital records.\n\n"
             "Questions to ask your lawyer\n- Can the blood test be challenged?\n\nWhere to get help\n- x")


def ask(question, model, prompts, **kw):
    return service.grounded_legal_response(question, "general", lambda p: prompts.append(p) or model, db=FakeDB(), **kw)


SCENARIOS = [
    ("I got pulled over and arrested for DUI, they took my blood at the hospital", "dui", "criminal"),
    ("Cops searched my car and found weed in the console, I'm charged with possession", "drugs", "criminal"),
    ("My daughter got caught shoplifting at Walmart, it's her first offense", "theft", "criminal"),
    ("My landlord filed a dispossessory because I'm two months behind on rent", "eviction", "civil"),
    ("I want to modify our custody order because my ex moved to Florida", "custody", "civil"),
    ("My probation officer says I violated probation for missing a drug test", "probation", "criminal"),
    ("I got a speeding ticket for 85 in a 65", "traffic", "criminal"),
    ("I'm being sued by a debt collector over an old credit card", "debt", "civil"),
    ("I was in police custody overnight and charged with battery", "criminal", "criminal"),
    ("I was convicted last month and want to appeal my conviction", "post_conviction", "criminal"),
    ("I got fired and my boss won't give me my final paycheck", "employment", "civil"),
]


@pytest.mark.parametrize("question,kind,family", SCENARIOS)
def test_own_situation_builds_a_plan(question, kind, family):
    p = dp.plan_for(question)
    assert p and p["status"] == "build" and p["case_type"] == kind and p["family"] == family


@pytest.mark.parametrize("question", [
    "How does First Offender work in Georgia?", "How long do I have to answer a lawsuit?", "What happens at a dispossessory hearing?",
    "Can a DUI be restricted from a record in Georgia?", "what are some things that could help my defense", "Can my landlord keep my deposit?"])
def test_informational_questions_keep_the_normal_answer(question):
    assert dp.plan_for(question) is None


@pytest.mark.parametrize("question,family", [("I got arrested last night what do I do", "criminal"), ("build my defense", "criminal"),
                                             ("I'm being sued", "civil")])
def test_vague_situations_ask_instead_of_guessing(question, family):
    p = dp.plan_for(question)
    assert p["status"] == "clarify" and p["family"] == family and 1 <= len(p["questions"]) <= 2


def test_clarify_answer_needs_no_model_call(wired):
    prompts = []
    r = ask("I got arrested last night what do I do", "should not be used", prompts)
    assert prompts == []
    assert r["defense_plan"]["status"] == "needs_details" and len(r["defense_plan"]["questions"]) == 2
    assert r["analysis"].startswith("Your Defense Plan\n\nQuick answer\n") and "What is the charge?" in r["analysis"]
    assert "Note: This is legal information, not legal advice." in r["analysis"] and r["follow_ups"] and r["authorities"] == []


def test_dui_plan_prompt_and_answer(wired):
    prompts = []
    r = ask("I got pulled over and arrested for DUI, they took my blood at the hospital", DUI_MODEL, prompts)
    p = prompts[0]
    assert "AUTOMATIC DEFENSE PLAN (DUI)" in p and "How they'd build the case against you" in p and "How to fight back" in p
    assert "The State cannot establish" in p and "They'd still need" in p and "Weak spots" in p
    assert "MOTIONS IN THE APP'S MOTION MAKER" in p and "Motion to suppress" in p
    for sec in ("40-6-391", "40-6-392", "40-5-67.1", "17-5-30"):
        assert f"O.C.G.A. § {sec}" in p
    a = r["analysis"]
    assert a.startswith("Your Defense Plan: DUI\n\nQuick answer\n")
    order = [a.index(h) for h in ("Quick answer", "How they'd build the case against you", "How to fight back", "Your rights",
                                  "Motions that could help", "Options to lessen the outcome", "Questions to ask your lawyer", "Where to get help")]
    assert order == sorted(order)
    assert r["defense_plan"] == {"status": "built", "case_type": "dui", "label": "DUI", "family": "criminal", "title": "Your Defense Plan: DUI"}
    assert r["suggested_motions"] and r["case_stage"] and any(m["draftable"] for m in r["suggested_motions"])
    assert "how_they_d_build_the_case_against_you" in r["sections"] and "how_to_fight_back" in r["sections"]
    assert r["citation_check"] == "passed" and "ALS hearing" in r["follow_ups"][0]
    assert a.rstrip().splitlines()[-1].startswith("Note: This is legal information, not legal advice.")


def test_civil_plan_has_civil_headings_and_no_criminal_motions(wired):
    prompts = []
    model = ("Quick answer\nPay or tender the rent if you can.\n\nHow they'd build the case against you\n- Likely claim: dispossessory for nonpayment.\n\n"
             "How to fight back\n- Demand: The landlord cannot show a proper demand for possession because none was made. Challenge: notice. Motion: Answer.\n\n"
             "Ways to challenge their case\n- Service of the summons (O.C.G.A. § 44-7-51).\n\nQuestions to ask your lawyer\n- Can I pay into court?\n\nWhere to get help\n- x")
    r = ask("My landlord filed a dispossessory because I'm two months behind on rent", model, prompts)
    assert "Ways to challenge their case" in prompts[0] and "Motions and filings that could help" in prompts[0] and "the landlord" in prompts[0]
    assert "O.C.G.A. § 44-7-52" in prompts[0]  # tender of rent as a defense, from the law database
    assert r["suggested_motions"] == [] and "case_stage" not in r and "Motions that could help" not in r["analysis"]
    assert r["analysis"].startswith("Your Defense Plan: Eviction") and r["defense_plan"]["family"] == "civil"


def test_build_my_defense_uses_earlier_facts():
    wrapped = "Conversation so far:\nUser: My son got a DUI last week and they took his blood\nAssistant: ...\n\nUser: Build my defense"
    p = dp.plan_for(wrapped)
    assert p["status"] == "build" and p["case_type"] == "dui" and "blood" in p["facts"]


def test_unverified_citation_retries_once_then_fails_closed(wired):
    prompts = []
    bad = DUI_MODEL.replace("O.C.G.A. § 42-8-60", "O.C.G.A. § 99-9-99")
    r = ask("I got pulled over and arrested for DUI, they took my blood at the hospital", bad, prompts)
    assert len(prompts) == 2 and "cite ONLY these sections" in prompts[1]
    assert r["citation_check"] == "failed_closed" and "99-9-99" not in r["analysis"]


def test_retry_success_keeps_the_plan(wired):
    prompts = []
    answers = iter([DUI_MODEL.replace("O.C.G.A. § 42-8-60", "O.C.G.A. § 99-9-99"), DUI_MODEL])
    r = service.grounded_legal_response("I got a DUI after a blood test", "general",
                                        lambda p: prompts.append(p) or next(answers), db=FakeDB())
    assert r["citation_check"] == "passed" and "How to fight back" in r["analysis"]


def test_cache_key_bumped_so_old_answers_are_not_served():
    import hashlib
    old = hashlib.sha256(f"v6\x00general\x00{answer_cache.normalize('x')}".encode()).hexdigest()
    assert answer_cache.key("x", "general") != old


def test_no_custody_or_guilt_assumptions_in_plan_prompt():
    block = dp.prompt_block({"status": "build", "case_type": "theft", "label": "Theft or shoplifting", "family": "criminal"})
    assert "without assuming facts" in block and "jail staff" not in block and "Never suggest lying" in block


# ---------------------------------------------------------------- uploaded papers
TRAFFIC_PAPER = {"readable": True, "document_type": "Georgia Uniform Traffic Citation", "summary": "A speeding citation for 84 in a 55 zone.",
                 "charges_or_claims": ["Speeding 84/55 O.C.G.A. 40-6-181"], "key_dates": ["Court date: December 15, 2026 9:00 AM"],
                 "helpful_flags": ["The officer's radar unit and calibration are not listed", "The location says only 'Hwy 78'"],
                 "extracted_text": "UNIFORM TRAFFIC CITATION ... 84 MPH IN 55 ...", "next_steps": [], "questions_for_lawyer": [], "photo_tips": ""}
EVICTION_PAPER = {"readable": True, "document_type": "Dispossessory Summons and Affidavit", "summary": "The landlord asks for possession for unpaid rent of $2,400.",
                  "charges_or_claims": ["Dispossessory for nonpayment of rent, $2,400"], "key_dates": ["Answer within 7 days of service"],
                  "helpful_flags": ["No date of the demand for possession is stated"], "extracted_text": "DISPOSSESSORY AFFIDAVIT ...",
                  "next_steps": [], "questions_for_lawyer": [], "photo_tips": ""}


def test_paper_type_detection():
    t = dp.document_plan(TRAFFIC_PAPER)
    e = dp.document_plan(EVICTION_PAPER)
    assert (t["status"], t["case_type"], t["source"]) == ("build", "traffic", "document")
    assert (e["status"], e["case_type"], e["family"]) == ("build", "eviction", "civil")
    unclear = dp.document_plan({"document_type": "Letter", "summary": "A letter.", "extracted_text": ""})
    assert unclear["status"] == "clarify"


def test_paper_plan_uses_facts_and_flags(wired):
    prompts = []
    plan = dp.document_plan(TRAFFIC_PAPER)
    model = ("Quick answer\nThe radar proof is missing.\n\nHow they'd build the case against you\n- Likely charge: speeding (O.C.G.A. § 40-6-181).\n\n"
             "How to fight back\n- Speed: The State cannot establish the speed because the radar calibration is not shown. Challenge: radar records. Motion: Discovery.\n\n"
             "What helps in your paperwork\n- The radar unit is not listed.\n\nQuestions to ask your lawyer\n- Can points be reduced?\n\nWhere to get help\n- x")
    r = service.grounded_legal_response(dp.document_situation(TRAFFIC_PAPER), "general", lambda p: prompts.append(p) or model, db=FakeDB(), plan=plan)
    p = prompts[0]
    assert "What helps in your paperwork" in p and "radar unit and calibration are not listed" in p and "December 15, 2026" in p
    assert "O.C.G.A. § 40-6-181" in p
    assert r["defense_plan"]["source"] == "document" and "What helps in your paperwork" in r["analysis"]


def test_civil_paper_gets_civil_help_not_a_public_defender(wired):
    plan = dp.document_plan(EVICTION_PAPER)
    r = service.grounded_legal_response(dp.document_situation(EVICTION_PAPER), "general", lambda p: "Quick answer\nx\n\nWhere to get help\n- x",
                                        db=FakeDB(), plan=plan)
    names = " ".join(h.get("name", "") for h in r["help_resources"]).lower()
    assert "public defender" not in names and "legal aid" in names


def test_reader_parses_helpful_flags():
    from app import document_reader as dr
    import json
    out = dr.parse_result(json.dumps({**EVICTION_PAPER}))
    assert out["helpful_flags"] == ["No date of the demand for possession is stated"]
    assert "What could help in this paper" in out["answer"]
    assert '"helpful_flags"' in dr.PROMPT


def test_documents_read_attaches_plan(monkeypatch, wired):
    from app import main
    prompts = []
    monkeypatch.setattr(main, "ask_fast", lambda p: prompts.append(p) or DUI_MODEL.replace("DUI", "speeding"))
    out = main._document_defense_plan(TRAFFIC_PAPER, "", FakeDB())
    assert out["status"] == "built" and out["answer"].startswith("Your Defense Plan: Traffic ticket")
    assert out["defense_plan"]["source"] == "document" and prompts


def test_documents_read_plan_failure_never_breaks_the_read(monkeypatch, wired):
    from app import main

    def boom(p):
        raise RuntimeError("down")
    monkeypatch.setattr(main, "ask_fast", boom)
    out = main._document_defense_plan(EVICTION_PAPER, "", FakeDB())
    assert out["status"] == "unavailable" and "Build my defense" in out["message"]
