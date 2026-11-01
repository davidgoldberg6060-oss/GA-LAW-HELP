from app.answer_format import clean_answer, laws_cited, SHORT_AMENDMENT_NOTE
from app.civil_topics import topic_sections
from app.slang import plain_terms
from app.grounded_legal_assistant import relevant_hits


def _topics(q):
    return topic_sections(q + " " + plain_terms(q), limit=40)


def test_self_defense_and_slang_fight_pull_justification_and_battery():
    for q in ("got into a fight defending my self but they wanna give me jail time help me",
              "got into a fade defending myself and 12 locked me up"):
        t = _topics(q)
        for s in ("16-3-21", "16-3-24.2", "16-3-23.1", "16-5-20", "16-5-23", "16-11-32"):
            assert s in t, (q, s)
        assert not any(s.startswith("42-4") for s in t)  # 'jail time' is not prison conditions


def test_prison_conditions_not_landlord():
    t = _topics("I'm in prison I have no water no good food and no bed")
    assert "42-4-32" in t and "42-4-4" in t
    assert not any(s.startswith("44-7") for s in t)
    assert any(s.startswith("44-7") for s in _topics("my landlord turned off the water"))


def test_shoplifting_ranks_16_8_14_first_and_other_slang():
    assert _topics("caught boosting at walmart")[0] == "16-8-14"
    assert "42-8-38" in _topics("my PO says I violated")
    assert "19-9-3" in _topics("my BM wont let me see my kids")
    assert "16-11-126" in _topics("I got popped with a strap")


def test_clean_answer_removes_markdown_meta_and_repeats_note_once():
    raw = ("### SHORT ANSWER\nGeorgia recognizes self-defense. The verified authorities provided in this system do not "
           "contain statutes regarding battery.\n* **Get a lawyer**\n### VERIFIED GEORGIA AUTHORITY\n* O.C.G.A. § 3-3-23.1\n"
           "Note: Georgia Code text shown is from the official 2022 edition (Public.Resource.Org release); some sections may "
           "have been amended since. Check the current law or ask a lawyer before relying on it.")
    out = clean_answer(raw, add_note=True)
    assert "#" not in out and "**" not in out and "system" not in out and "3-3-23.1" not in out
    assert out.startswith("Short answer") and "• Get a lawyer" in out
    assert out.count("2022 edition") == 1 and SHORT_AMENDMENT_NOTE in out


def test_relevance_filter_drops_unrelated_persisted_hits():
    hits = [{"corpus": "persisted_authorities", "citation": "Ga. Comp. R. & Regs. R. 130-7-.04", "title": "Fines for cosmetology", "excerpt": "salon license"},
            {"corpus": "persisted_authorities", "citation": "O.C.G.A. § 16-3-21", "title": "Use of force in defense of self or others", "excerpt": ""}]
    kept = relevant_hits(hits, "fight self defense", {"16-3-21"})
    assert [h["citation"] for h in kept] == ["O.C.G.A. § 16-3-21"]


def test_laws_cited_compact():
    out = laws_cited([{"citation": "O.C.G.A. § 16-3-21 (text as of 2022 edition)", "citation_raw": "O.C.G.A. § 16-3-21",
                       "title": "O.C.G.A. § 16-3-21. Use of force in defense of self or others; evidence of belief", "id": 5}])
    assert out == [{"citation": "O.C.G.A. § 16-3-21", "title": "Use of force in defense of self or others", "id": 5}]


def test_internal_labels_and_empty_plain_headings_removed():
    raw = ("How it works in Georgia\n• Factual premise: Your PO reported a violation.\n• Unverified issues: We do not know why.\n"
           "Deadlines and costs\nWhere to get help\n• Call legal aid.")
    out = clean_answer(raw)
    assert "Factual premise" not in out and "Unverified issues" not in out and "• Your PO reported" in out
    assert "Deadlines and costs" not in out and "Where to get help" in out


def test_prison_answers_always_include_written_sick_call():
    from app.grounded_legal_assistant import ensure_sick_call, SICK_CALL_STEP
    a = "Steps you can take\n• File a grievance.\n\nNote: x"
    out = ensure_sick_call(a, "I'm in prison I have no water no good food and no bed")
    assert out.split("\n")[1] == SICK_CALL_STEP
    assert ensure_sick_call(a, "my landlord shut off the water") == a


def test_echoed_instructions_and_reasoning_labels_are_dropped():
    raw = ("Short answer\nYou are stating serious issues, which are currently allegations that need verification. Georgia law requires meals.\n"
           "Steps you can take\n• ALWAYS include as its own step: put in a written sick-call request.\n• File a grievance.\n"
           "How it works\nThe factual premise is your report of no water. Under the law, meals are required.")
    out = clean_answer(raw)
    assert "ALWAYS" not in out and "factual premise" not in out and "need verification" not in out
    assert "Georgia law requires meals." in out and "File a grievance" in out


def test_sick_call_only_for_conditions_questions():
    from app.grounded_legal_assistant import ensure_sick_call
    a = "Steps you can take\n• Ask for the case file."
    assert ensure_sick_call(a, "my brother is in prison doing 15 years, how can he get out early") == a
