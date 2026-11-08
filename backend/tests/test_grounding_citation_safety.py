"""Retrieval uses the latest user message; answers citing unretrieved law fail closed; /public/ask is grounded."""
from fastapi.testclient import TestClient

from app import grounded_legal_assistant as service
from app.civil_topics import topic_sections

WRAP = ("Continue a focused STANDALONE ASSISTANT legal-information conversation. Stay within Georgia law, rights, "
        "police encounters, criminal/civil legal procedure, motions, sentencing, incarceration/post-conviction issues, appeals.\n"
        "Conversation so far (recent context only):\nUser: hi\nSTANDALONE ASSISTANT: hello\n\nUser: ")
PRISON_SECTIONS = {"42-4-4", "42-4-32", "42-5-2"}


def _hit(section, excerpt="Stored authority text."):
    return {"title": "Code section", "citation": f"O.C.G.A. § {section}", "corpus": "statutes", "verification_status": "verified",
            "source_url": "https://law.example.gov/" + section, "excerpt": excerpt}


def _run(monkeypatch, query, answer, hits):
    seen = {}
    def fake_search(q, mode, limit):
        seen["search"] = q
        return {"hits": hits}
    monkeypatch.setattr(service, "search_internal", fake_search)
    monkeypatch.setattr(service, "relevant_hits", lambda h, s, t: h)
    prompts = []
    result = service.grounded_legal_response(query, "general", lambda p: prompts.append(p) or answer)
    return result, seen, prompts


# --- retrieval contamination ---------------------------------------------------------------------
def test_wrapped_self_defense_and_eviction_do_not_pull_jail_law(monkeypatch):
    for q, want in (("Can I claim self defense?", "16-3-21"), ("My landlord filed a dispossessory", "44-7-50")):
        result, seen, prompts = _run(monkeypatch, WRAP + q, "General info.", [])
        assert "incarceration" not in seen["search"]
        assert q in seen["search"]
        assert "incarceration" in prompts[0]  # model still gets the conversation context
        secs = set(topic_sections(service.search_text_for(service.retrieval_question(WRAP + q)), limit=40))
        assert want in secs and not (secs & PRISON_SECTIONS)


def test_explicit_jail_question_still_retrieves_jail_law():
    secs = set(topic_sections(service.search_text_for(service.retrieval_question(WRAP + "My son is in jail with no medical care")), limit=40))
    assert secs & PRISON_SECTIONS


# --- citation validation -----------------------------------------------------------------------
def test_real_retrieved_citation_passes(monkeypatch):
    result, _, _ = _run(monkeypatch, "self defense?", "Under O.C.G.A. § 16-3-21 force may be justified.", [_hit("16-3-21")])
    assert result["citation_check"] == "passed" and "16-3-21" in result["analysis"]


def test_nonexistent_citation_fails_closed_without_confident_claim(monkeypatch):
    bad = "You must appeal within 30 days under O.C.G.A. § 46-1-23."
    result, _, _ = _run(monkeypatch, "appeal deadline?", bad, [_hit("17-17-12")])
    assert result["citation_check"] == "failed_closed"
    assert result["unsupported_citations"] == ["46-1-23"]
    assert "46-1-23" not in result["analysis"] and "30 days" not in result["analysis"]
    assert "couldn't verify" in result["analysis"]


def test_malformed_citation_forms_are_detected():
    assert service.citation_check("See OCGA 5-6-38 and Code Section 40-5-67.1(g).", [])["unsupported"] == ["5-6-38", "40-5-67.1"]


def test_retrieval_failure_with_cited_law_fails_closed(monkeypatch):
    result, _, _ = _run(monkeypatch, "question", "Per O.C.G.A. § 9-3-33 you have two years.", [])
    assert result["citation_check"] == "failed_closed"
    assert "9-3-33" not in result["analysis"]


def test_day_count_missing_from_source_text_gets_warning(monkeypatch):
    src = _hit("40-5-67.1", "Chemical tests; implied consent notices ...")  # excerpt truncated before (g)(1)
    result, _, _ = _run(monkeypatch, "ALS hearing?", "Request a hearing within 30 business days under O.C.G.A. § 40-5-67.1.", [src])
    assert result["deadline_warning"] is True and "could not be confirmed" in result["analysis"]
    ok = _hit("40-5-67.1", "a request, in writing, for a hearing within 30 days from the date of personal notice")
    result, _, _ = _run(monkeypatch, "ALS hearing?", "Request a hearing within 30 days under O.C.G.A. § 40-5-67.1.", [ok])
    assert result["deadline_warning"] is False


# --- legacy endpoint ---------------------------------------------------------------------------
def test_legacy_public_ask_is_grounded_and_keeps_schema(monkeypatch):
    from app import legacy_main
    from app.main import app
    calls = []
    monkeypatch.setattr(legacy_main, "grounded_public_ask", lambda q, db: calls.append(q) or {
        "analysis": "grounded answer", "laws_cited": [], "citation_check": "passed", "grounded_authority_count": 0})
    with TestClient(app) as client:
        acct = client.post("/auth/register", json={"email": "ask@example.com", "password": "ask-account-secure-password"}).json()
        h = {"Authorization": "Bearer " + acct["access_token"]}
        r = client.post("/public/ask", json={"question": "What are my rights?"}, headers=h)
        assert r.status_code == 200, r.text
        body = r.json()
        assert {"question", "answer", "notice"} <= set(body) and body["answer"] == "grounded answer"
        assert calls == ["What are my rights?"]
        assert client.post("/public/ask", json={"question": ""}, headers=h).status_code == 400
        assert client.post("/public/ask", json={"question": "x"}).status_code in (401, 403)


def test_legacy_public_ask_remains_rate_limited():
    from app.anonymous_access import is_ai_path
    assert is_ai_path("POST", "/public/ask")
