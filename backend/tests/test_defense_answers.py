"""Defense-first answers: broad defense overview, defense angles for every criminal question, and relevant motions
from the catalog with only verified Georgia citations. No custody or fact assumptions."""
import contextlib
import json
import re

import pytest

from app import defense_help as dh
from app import grounded_legal_assistant as service
from app.civil_topics import follow_ups
from app.help_resources import lawyer_questions, route

Q = "what are some things that could help my defense"
WRAP = ("Continue a focused STANDALONE ASSISTANT legal-information conversation. Stay within Georgia law, rights, "
        "incarceration/post-conviction issues, appeals.\nConversation so far (recent context only):\nUser: hi\nSTANDALONE ASSISTANT: hello\n\nUser: ")
TITLES = {"16-3-20": "Justification", "16-3-21": "Use of force in defense of self or others", "16-3-23.1": "No duty to retreat",
          "16-3-24.2": "Immunity from prosecution", "16-3-28": "Affirmative defenses", "17-5-30": "Motion to suppress evidence illegally seized generally",
          "17-5-21": "Grounds for issuance of search warrant", "24-8-824": "Only voluntary confessions admissible", "17-16-4": "Disclosure required by prosecuting attorney and defendant",
          "17-16-1": "Definitions", "17-16-2": "Applicability of article", "17-7-170": "Demand for speedy trial", "17-7-171": "Time for demand for speedy trial in capital cases",
          "17-3-1": "Generally", "17-7-110": "Time for filing pretrial motions", "17-7-111": "Demurrers and special pleas to be in writing",
          "17-7-54": "Form of indictment by grand jury", "16-3-25": "Entrapment", "16-3-5": "Mistake of fact", "16-3-2": "Mental capacity",
          "17-16-5": "Alibi witnesses", "42-8-60": "Probation prior to adjudication of guilt", "16-13-2": "Conditional discharge", "15-1-15": "Drug court divisions",
          "8-8-8": "Not a real section"}
MISSING = {"8-8-8"}


def hit(sec, status="verified"):
    return {"corpus": "persisted_authorities", "title": TITLES.get(sec, sec), "citation": f"O.C.G.A. § {sec}",
            "source_url": "https://archive.org/download/gov.ga.ocga.2018/release86.2022", "verification_status": status,
            "excerpt": f"Text of {sec} ({TITLES.get(sec, '')}).", "record_type": "statute"}


class FakeDB:
    @contextlib.contextmanager
    def begin_nested(self):
        yield


@pytest.fixture
def wired(monkeypatch):
    """Retrieval returns the live-app failure pattern: only the self-defense statute family for 'defense'."""
    import app.charge_check_service as ccs
    monkeypatch.setattr(service, "_hybrid_retrieval", lambda q, m, db, l: {"hits": [hit(s) for s in ("16-3-20", "16-3-21", "16-3-23.1", "16-3-24.2", "16-3-28")]})
    monkeypatch.setattr(ccs, "lookup_sections", lambda db, secs: [hit(s) for s in secs if s not in MISSING])
    monkeypatch.setattr(service, "exact_citation_results", lambda db, cites: [])
    prompts = []
    return prompts


MODEL = ("Short answer\nThe strongest defense depends on the charge and the facts. What is the charge?\n\n"
         "How it works in Georgia\nChallenging the evidence:\n- A motion to suppress under O.C.G.A. § 17-5-30 may help if a search was illegal.\n"
         "Ways to lessen the outcome:\n- First Offender (O.C.G.A. § 42-8-60) may apply if there is no prior felony.\n\n"
         "Steps you can take\n- Tell jail staff and other inmates nothing.\n\nDeadlines and costs\n- Ask about deadlines.\n\nWhere to get help\n- x")


def run(wired, question=Q, model=MODEL):
    return service.grounded_legal_response(WRAP + question, "general", lambda p: wired.append(p) or model, db=FakeDB())


def test_detection_broad_vs_self_defense_vs_civil():
    assert dh.is_broad_defense(Q) and dh.is_broad_defense("How can I beat this case?")
    assert dh.is_broad_defense("what is the best defense for a theft charge")
    assert not dh.is_broad_defense("Can I claim self-defense after a fight?")
    assert not dh.is_broad_defense("My landlord is evicting me, what defenses do I have?")
    assert not dh.is_broad_defense("How do I find a defense attorney?")
    assert dh.is_criminal("I was charged with shoplifting") and not dh.is_criminal("my landlord kept my deposit")


def test_exact_question_gets_broad_defense_retrieval_not_just_self_defense(wired):
    r = run(wired)
    p = wired[0]
    for sec in ("17-5-30", "24-8-824", "17-16-4", "17-7-170", "17-3-1", "16-3-25", "16-3-5", "16-3-2", "42-8-60", "16-13-2", "15-1-15"):
        assert f"O.C.G.A. § {sec}\n" in p, sec
    # use-of-force statutes stay out when no force is mentioned
    for sec in ("16-3-21", "16-3-23.1", "16-3-24.2", "16-3-28"):
        assert f"O.C.G.A. § {sec}\n" not in p, sec
    assert "BROAD DEFENSE QUESTION" in p and "depends on the charge and the facts" in p
    assert "Ways to fight the evidence:" in p and "Ways to lessen the outcome:" in p
    assert r["citation_check"] == "passed"


def test_exact_question_answer_sections_and_no_custody_assumption(wired):
    r = run(wired)
    a = r["analysis"]
    assert "Steps you can take" not in a and "jail staff" not in a and "inmates" not in a
    order = [a.index(h) for h in ("Short answer", "How it works in Georgia", "Motions that could help", "Questions to ask your lawyer", "Where to get help")]
    assert order == sorted(order)
    qs = a.split("Questions to ask your lawyer")[1].split("Deadlines and costs")[0]
    assert "motions" in qs.lower() and qs.count("?") >= 4 and "custody" not in qs.lower()
    assert r["case_stage"] == "pretrial"
    assert r["follow_ups"] if "follow_ups" in r else True
    assert follow_ups(Q) == list(dh.BROAD_FOLLOW_UPS)
    assert [h["id"] for h in route(Q)][:1] == ["public_defender"]


def test_defense_question_returns_relevant_motions_with_verified_citations(wired):
    r = run(wired)
    keys = [m["key"] for m in r["suggested_motions"]]
    assert {"suppress", "suppress_statements", "speedy_trial", "first_offender"} <= set(keys)
    assert "immunity" not in keys  # no force mentioned
    section = r["analysis"].split("Motions that could help")[1].split("Questions to ask your lawyer")[0]
    assert "Motion to suppress evidence (O.C.G.A. § 17-5-30" in section and "How it can help:" in section
    assert "Demand for speedy trial (O.C.G.A. § 17-7-170" in section
    # every citation shown in the motions section is verified and listed in Laws cited
    cited = {c["citation"] for c in r["laws_cited"]}
    for cite in re.findall(r"O\.C\.G\.A\. § [\d.-]+", section):
        assert cite in cited
    # case-law-only authorities are never shown
    assert "Brady v." not in r["analysis"] and "Jackson v. Denno" not in r["analysis"] and "U.S." not in section
    assert "Open My Case" in section


def test_motion_dropped_when_its_law_cannot_be_verified(monkeypatch):
    bad = [{"citation": "O.C.G.A. § 17-5-30", "verification_status": "unverified"}]
    got = dh.suggested_motions("police searched my car without a warrant", lambda cites: [h for h in [hit(s) for s in cites if re.fullmatch(r"[\d.-]+", s)] if h["citation"] != "O.C.G.A. § 17-5-30" and h["citation"] != "O.C.G.A. § 17-5-21"])
    assert "suppress" not in [m["key"] for m in got]
    assert bad  # documented shape


@pytest.mark.parametrize("question,expected", [
    ("I was charged with shoplifting, what can I do?", {"suppress", "speedy_trial", "first_offender"}),
    ("Police searched my car without a warrant and found weed", {"suppress", "conditional_discharge"}),
    ("I got a DUI, what can I do?", {"suppress_chemical_test"}),
    ("I defended myself in a fight and got charged with battery", {"immunity"}),
    ("I told the detectives everything before they read me my rights", {"suppress_statements"}),
    ("I was found guilty at trial last week", {"new_trial", "appeal"}),
    ("How can I get off probation early?", {"early_termination_probation"}),
    ("Can I expunge my record?", {"record_restriction"}),
    ("My criminal case has been waiting for two years with no trial date", {"speedy_trial", "speedy_trial_constitutional"}),
])
def test_criminal_questions_get_relevant_motions(question, expected):
    assert expected <= set(dh.motion_keys(question)), dh.motion_keys(question)


def test_post_conviction_questions_do_not_get_pretrial_motions_and_civil_gets_none():
    keys = dh.motion_keys("I was found guilty at trial last week")
    assert not {"suppress", "speedy_trial", "general_demurrer"} & set(keys)
    assert dh.motion_keys("My landlord is evicting me, what defenses do I have?") == []
    assert dh.motion_keys("How do I get a divorce?") == []


def test_every_criminal_question_gets_defense_focus_prompt(wired):
    # A general (informational) criminal question; a user's own situation gets the Defense Plan (test_defense_plan.py).
    run(wired, "What happens after a shoplifting charge in Georgia?", "Short answer\nx\n\nHow it works in Georgia\ny")
    assert "DEFENSE FOCUS" in wired[-1] and "BROAD DEFENSE QUESTION" not in wired[-1]
    assert "say plainly how it can help and when it applies" in wired[-1]


def test_civil_question_has_no_defense_block_or_motions(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda q, m, l: {"hits": []})
    prompts = []
    r = service.grounded_legal_response("My landlord won't return my security deposit", "general", lambda p: prompts.append(p) or "Short answer\nx")
    assert "DEFENSE FOCUS" not in prompts[0] and r["suggested_motions"] == [] and "Motions that could help" not in r["analysis"]


def test_catalog_is_complete_and_safe():
    data = json.load(open(dh.CATALOG_PATH, encoding="utf-8"))
    motions = data["motions"]
    assert len(motions) >= 60 and len({m["key"] for m in motions}) == len(motions)
    from app.motions import BY_KEY
    stages = {"arrested", "pretrial", "plea", "trial", "sentenced", "appeal", "prison", "probation", "record"}
    for m in motions:
        assert m["name"] and m["purpose"] and m["when_it_applies"] and m["how_it_helps"], m["key"]
        assert set(m["stages"]) <= stages and m["goal"] in {"beat_case", "less_time", "better_outcome"}
        assert not m["template_key"] or m["template_key"] in BY_KEY
        assert all(re.fullmatch(r"\d{1,2}-\d{1,3}-\d+(\.\d+)?", s) for s in m["ocga"])
        assert not m["deadline_source"] or re.fullmatch(r"\d{1,2}-\d{1,3}-\d+(\.\d+)?", m["deadline_source"])
        text = " ".join([m["purpose"], m["when_it_applies"], m["how_it_helps"]]).lower()
        assert "your loved one" not in text and "inmate" not in text
        re.compile(m["triggers"])
    # each requested family is present
    keys = {m["key"] for m in motions}
    for k in ("bond", "bond_reduction", "suppress", "general_demurrer", "special_demurrer", "quash", "speedy_trial", "speedy_trial_constitutional",
              "discovery", "brady", "suppress_statements", "severance", "change_of_venue", "in_limine", "recusal", "immunity", "statute_of_limitations",
              "double_jeopardy", "compel_discovery", "informant", "independent_testing", "competency", "expert_funds", "withdraw_plea",
              "directed_verdict", "mistrial", "new_trial", "arrest_of_judgment", "sentence_mod", "void_sentence", "out_of_time_appeal", "habeas",
              "extraordinary_mnt", "dna_testing", "retroactive_first_offender", "record_restriction", "early_termination_probation", "parole",
              "time_credit", "medical_reprieve", "federal_habeas"):
        assert k in keys, k


def test_lawyer_questions_for_broad_defense():
    qs = lawyer_questions(Q)
    assert qs == list(dh.BROAD_LAWYER_QUESTIONS) and all(q.endswith("?") for q in qs)


def test_charge_question_follow_ups_stay_on_defense():
    fu = follow_ups("I was charged with shoplifting, what can I do?", "Record restriction and First Offender may help your record.")
    assert fu == list(dh.CHARGE_FOLLOW_UPS)
    assert follow_ups("My security deposit wasn't returned") and "defenses" not in " ".join(follow_ups("My security deposit wasn't returned"))
