from app import grounded_legal_assistant as service


def _retrieval(status="verified"):
    return {
        "hits": [{
            "title": "Example v. State",
            "citation": "123 Ga. 456",
            "corpus": "cases",
            "verification_status": status,
            "excerpt": "Stored authority text.",
        }],
        "coverage_notice": "Internal corpus only.",
    }


def test_grounded_response_supplies_verified_authority_to_ai(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval())
    prompts = []
    result = service.grounded_legal_response(
        "Police searched the car.", "case_analysis", lambda prompt: prompts.append(prompt) or "analysis"
    )
    assert result["analysis"] == "analysis"
    assert result["grounded_authority_count"] == 1
    assert "123 Ga. 456" in prompts[0]
    assert "never create a citation" in prompts[0]


def test_unverified_only_results_never_trigger_ai_analysis(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval("unverified"))
    called = False

    def ask_ai(_prompt):
        nonlocal called
        called = True
        return "should not run"

    result = service.grounded_legal_response("Question", "talk_to_me", ask_ai)
    assert called is False
    assert result["analysis"] is None
    assert result["grounded_authority_count"] == 0
    assert "will not invent authority" in result["coverage_notice"]


def test_grounded_prompt_labels_user_facts_unverified(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval("official"))
    prompts = []
    service.grounded_legal_response("Officer said I consented.", "rights", lambda prompt: prompts.append(prompt) or "ok")
    assert "not independently verified" in prompts[0]
    assert "allegations/facts to be verified" in prompts[0]


def test_unsupported_mode_is_rejected_before_ai(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval())
    try:
        service.grounded_legal_response("Question", "case_lookup", lambda prompt: "bad")
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:
        raise AssertionError("unsupported grounded mode should fail")
