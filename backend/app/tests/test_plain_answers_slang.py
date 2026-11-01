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
