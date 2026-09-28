from app import grounded_legal_assistant as gla


def verified_hit(**overrides):
    hit = {
        "title": "Example verified Georgia authority",
        "citation": "Example Citation",
        "source_url": "https://www.gasupreme.us/example",
        "verification_status": "official",
        "currency_status": "unknown",
        "precedential_status": "unknown",
        "status_checked_at": None,
        "status_source_url": None,
        "negative_treatment": [],
        "corpus": "cases",
        "excerpt": "Stored excerpt only.",
    }
    hit.update(overrides)
    return hit


def test_talk_to_me_prompt_requires_live_safety_sections(monkeypatch):
    monkeypatch.setattr(gla, "search_internal", lambda *args, **kwargs: {"hits": [verified_hit()], "coverage_notice": "indexed"})
    captured = {}

    def fake_ai(prompt):
        captured["prompt"] = prompt
        return "grounded response"

    result = gla.grounded_legal_response("Officer asked to search my car.", "talk_to_me", fake_ai)
    prompt = captured["prompt"]
    assert result["analysis"] == "grounded response"
    for section in (
        "WHAT APPEARS TO BE HAPPENING",
        "SAFEST IMMEDIATE STEPS",
        "YOUR RIGHTS",
        "WHAT LAW ENFORCEMENT MAY / MAY NOT DO",
        "WHAT TO SAY OR DO",
        "VERIFIED GEORGIA AUTHORITY",
        "IMPORTANT LIMITATIONS",
    ):
        assert section in prompt
    assert "speech-to-text transcription errors" in prompt
    assert "do not encourage resistance" in prompt
    assert "recording is lawful" in prompt


def test_talk_to_me_answers_without_traceable_authority_but_forbids_fake_citations(monkeypatch):
    monkeypatch.setattr(gla, "search_internal", lambda *args, **kwargs: {
        "hits": [verified_hit(source_url="", verification_status="unverified")],
        "coverage_notice": "not enough",
    })
    captured = {}

    def fake_ai(prompt):
        captured["prompt"] = prompt
        return "WHAT APPEARS TO BE HAPPENING\nGeneral explanation.\nSAFEST IMMEDIATE STEPS\nStay safe.\nYOUR RIGHTS\nNeeds Georgia verification.\nWHAT LAW ENFORCEMENT MAY / MAY NOT DO\nNeeds verification.\nWHAT TO SAY OR DO\nAsk for counsel.\nVERIFIED GEORGIA AUTHORITY\nNone retrieved.\nIMPORTANT LIMITATIONS\nGeneral information only."

    result = gla.grounded_legal_response("What happens if I am charged with murder?", "talk_to_me", fake_ai)
    prompt = captured["prompt"]
    assert result["analysis"] is not None
    assert result["grounded_authority_count"] == 0
    assert result["sections"]["your_rights"] == "Needs Georgia verification."
    assert "general legal information" in prompt
    assert "MUST NOT invent a citation" in prompt
    assert "will not invent" in result["coverage_notice"]


def test_talk_to_me_rejects_negative_authority_as_verified_support_but_still_answers(monkeypatch):
    monkeypatch.setattr(gla, "search_internal", lambda *args, **kwargs: {
        "hits": [verified_hit(currency_status="overruled", negative_treatment=["overruled"])],
        "coverage_notice": "indexed",
    })
    captured = {}

    def fake_ai(prompt):
        captured["prompt"] = prompt
        return "general answer"

    result = gla.grounded_legal_response("Can they search this?", "talk_to_me", fake_ai)
    assert result["analysis"] == "general answer"
    assert result["grounded_authority_count"] == 0
    assert "Example Citation" not in captured["prompt"]


def test_unknown_status_is_exposed_to_ai_not_upgraded(monkeypatch):
    monkeypatch.setattr(gla, "search_internal", lambda *args, **kwargs: {"hits": [verified_hit()], "coverage_notice": "indexed"})
    captured = {}

    def fake_ai(prompt):
        captured["prompt"] = prompt
        return "analysis"

    gla.grounded_legal_response("What can I say?", "talk_to_me", fake_ai)
    prompt = captured["prompt"]
    assert "Currency: unknown" in prompt
    assert "Precedential status: unknown" in prompt
    assert "do not fill it from memory" in prompt