from app import grounded_legal_assistant as service


def _retrieval(status="verified", citation="123 Ga. 456", source_url="https://courts.example.gov/opinion", **metadata):
    hit = {
        "title": "Example v. State",
        "citation": citation,
        "corpus": "cases",
        "verification_status": status,
        "source_url": source_url,
        "excerpt": "Stored authority text.",
    }
    hit.update(metadata)
    return {"hits": [hit], "coverage_notice": "Internal corpus only."}


def test_grounded_response_supplies_traceable_verified_authority_to_ai(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval())
    prompts = []
    result = service.grounded_legal_response("Police searched the car.", "case_analysis", lambda prompt: prompts.append(prompt) or "analysis")
    assert result["analysis"] == "analysis"
    assert result["grounded_authority_count"] == 1
    assert "123 Ga. 456" in prompts[0]
    assert "https://courts.example.gov/opinion" in prompts[0]
    assert "never create a citation" in prompts[0]
    assert "current, binding, controlling, or precedential" in prompts[0]


def test_unverified_only_results_offer_general_guidance_without_citing_hit(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval("unverified"))
    called = False
    def ask_ai(_prompt):
        nonlocal called
        called = True
        return "should not run"
    result = service.grounded_legal_response("Question", "talk_to_me", ask_ai)
    assert called is True
    assert result["analysis"] == "should not run"
    assert result["grounded_authority_count"] == 0
    assert "will not invent" in result["coverage_notice"]


def test_verified_label_without_citation_is_not_grounding_authority(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval(citation=""))
    result = service.grounded_legal_response("Question", "rights", lambda prompt: "should not run")
    assert result["analysis"] == "should not run"
    assert result["grounded_authority_count"] == 0


def test_verified_label_without_https_source_is_not_grounding_authority(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda query, mode, limit: _retrieval(source_url="http://example.invalid/opinion"))
    result = service.grounded_legal_response("Question", "motions", lambda prompt: "should not run")
    assert result["analysis"] == "should not run"
    assert result["grounded_authority_count"] == 0


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


def test_overruled_currency_never_enters_grounding_context(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda q, m, l: _retrieval(currency_status="overruled"))
    called = False
    def ask_ai(_prompt):
        nonlocal called
        called = True
        return "bad"
    result = service.grounded_legal_response("Question", "case_analysis", ask_ai)
    assert called is True
    assert result["grounded_authority_count"] == 0
    assert "No matching traceable verified" in result["coverage_notice"]


def test_negative_treatment_list_blocks_authority(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda q, m, l: _retrieval(negative_treatment=["vacated"]))
    result = service.grounded_legal_response("Question", "rights", lambda prompt: "bad")
    assert result["analysis"] == "bad"
    assert result["grounded_authority_count"] == 0


def test_unknown_currency_is_disclosed_not_invented(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda q, m, l: _retrieval(currency_status="unknown", precedential_status="unknown"))
    prompts = []
    result = service.grounded_legal_response("Question", "motions", lambda prompt: prompts.append(prompt) or "limited analysis")
    assert result["grounded_authority_count"] == 1
    assert "Currency: unknown" in prompts[0]
    assert "Precedential status: unknown" in prompts[0]
    assert "do not fill it from memory" in prompts[0]


def test_positive_status_metadata_is_passed_to_ai(monkeypatch):
    monkeypatch.setattr(service, "search_internal", lambda q, m, l: _retrieval(currency_status="current", precedential_status="binding", status_checked_at="2026-09-27T12:00:00Z", status_source_url="https://courts.ga.gov/status"))
    prompts = []
    service.grounded_legal_response("Question", "talk_to_me", lambda prompt: prompts.append(prompt) or "analysis")
    prompt = prompts[0]
    assert "Currency: current" in prompt
    assert "Precedential status: binding" in prompt
    assert "2026-09-27T12:00:00Z" in prompt
    assert "https://courts.ga.gov/status" in prompt
