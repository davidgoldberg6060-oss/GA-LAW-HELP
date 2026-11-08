"""Verified 'Where to get help' routing, 'Questions to ask your lawyer' section, and no assumed custody/family."""
import re
from app import grounded_legal_assistant as service
from app.help_resources import R, ensure_lawyer_questions, replace_help_section, route

WRAP = ("Continue a focused STANDALONE ASSISTANT legal-information conversation. Stay within Georgia law, rights, "
        "incarceration/post-conviction issues, appeals.\nConversation so far (recent context only):\nUser: hi\nSTANDALONE ASSISTANT: hello\n\nUser: ")
MODEL = ("Short answer\n• x\n\nHow it works in Georgia\n• Under O.C.G.A. § 16-3-24.2 a person may seek immunity; the person in custody may ...\n\n"
         "Steps you can take\n• Remind your loved one in custody to remain silent.\n\nDeadlines and costs\n• y\n\n"
         "Where to get help\n• Public defender if your loved one qualifies. State Bar referral.\n\nNote: Georgia Code text is from the 2022 edition.")


def ids(q):
    return [r["id"] for r in route(q)]


def test_catalogue_entries_have_https_sources_and_no_invented_fields():
    for r in R.values():
        assert r["url"].startswith("https://") and r["source"].startswith("https://")
        assert r["phone"] is None or re.fullmatch(r"[\d-]+", r["phone"])


def test_self_defense_routes_to_criminal_help_only():
    got = ids(WRAP + "Can I get a pretrial immunity hearing for self defense?")
    assert got[:2] == ["public_defender", "lawyer_directory"]
    assert not {"gdc_family", "atlanta_legal_aid", "glsp"} & set(got)


def test_civil_county_routing_uses_only_named_county():
    assert "atlanta_legal_aid" in ids("Landlord filed a dispossessory in Cobb County") and "glsp" not in ids("Landlord filed a dispossessory in Cobb County")
    assert "glsp" in ids("Landlord eviction in Bibb County") and "atlanta_legal_aid" not in ids("Landlord eviction in Bibb County")
    both = ids("My landlord wants to evict me")
    assert {"atlanta_legal_aid", "glsp"} <= set(both) and "public_defender" not in both


def test_topic_specific_resources():
    assert "dds_als" in ids("I was arrested for DUI, what about my license?")
    assert "consumer_protection" in ids("A car dealer scam, can I get a refund?")
    assert ids("He hit me, can I get a protective order?")[0] == "dv_hotline"
    assert "gdc_family" in ids("My son is in prison and has no medical care")


def test_unknown_question_gets_honest_fallback_not_generic_junk():
    assert ids("What is the capital of France?") == []
    text, res = replace_help_section("Short answer\n• x", "What is the capital of France?")
    assert res == [] and "don't have a specific verified resource" in text


def test_model_help_section_is_replaced_and_note_kept():
    text, res = replace_help_section(MODEL, WRAP + "Can I get a pretrial immunity hearing for self defense?")
    assert "if your loved one qualifies" not in text and "State Bar referral" not in text
    assert "does not refer clients" in text and text.rstrip().endswith("2022 edition.")
    assert "16-3-24.2" in text  # law text untouched


def test_steps_replaced_by_lawyer_questions_without_custody_assumption():
    q = WRAP + "Can I get a pretrial immunity hearing for self defense?"
    text = ensure_lawyer_questions(replace_help_section(MODEL, q)[0], q)
    assert "Steps you can take" not in text and "Questions to ask your lawyer" in text
    section = text.split("Questions to ask your lawyer")[1].split("Deadlines and costs")[0]
    assert "immunity hearing apply" in section and section.count("?") >= 3
    assert "loved one" not in section.lower() and "custody" not in section.lower()


def test_model_written_question_section_kept_and_steps_dropped():
    a = "Short answer\n• x\n\nSteps you can take\n• do things\n\nQuestions to ask your lawyer\n• Does this apply to me?\n\nDeadlines and costs\n• y"
    out = ensure_lawyer_questions(a, "eviction")
    assert "Steps you can take" not in out and "Does this apply to me?" in out


def test_prompt_is_neutral_and_separates_instructions_from_facts():
    prompts = []
    import pytest
    mp = pytest.MonkeyPatch()
    mp.setattr(service, "search_internal", lambda q, m, l: {"hits": []})
    try:
        r = service.grounded_legal_response(WRAP + "Can I get a pretrial immunity hearing for self defense?", "general", lambda p: prompts.append(p) or MODEL)
    finally:
        mp.undo()
    p = prompts[0]
    assert "most users are family or friends" not in p and "by default say the person in custody" not in p
    assert "do not assume the user, or anyone else, is arrested, in custody" in p
    assert "not facts about the user" in p
    assert "Questions to ask your lawyer" in p and "Steps you can take" not in p
    assert "State Bar of Georgia lawyer referral" not in p
    assert [h["id"] for h in r["help_resources"]][:1] == ["public_defender"]
    assert "Steps you can take" not in r["analysis"] and "Questions to ask your lawyer" in r["analysis"]


def test_explicit_family_jail_question_keeps_family_guidance_and_resources():
    q = WRAP + "My brother is in jail and they won't give him medical care"
    assert "gdc_family" in ids(q)
    assert "loved one" in service._STYLE  # explicit family case still allowed by the instructions
