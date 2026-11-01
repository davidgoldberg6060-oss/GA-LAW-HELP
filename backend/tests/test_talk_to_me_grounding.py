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
        "What's happening",
        "Stay safe right now",
        "Your rights",
        "What police can and can't do",
        "What to say or do",
    ):
        assert section in prompt
    assert "speech-to-text errors" in prompt.lower()
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
        return "### WHAT'S HAPPENING\nGeneral explanation.\nStay safe right now\nStay safe.\n**Your rights**\nNeeds Georgia verification.\nWhat police can and can't do\nNeeds verification.\nWhat to say or do\nAsk for counsel."

    result = gla.grounded_legal_response("What happens if I am charged with murder?", "talk_to_me", fake_ai)
    prompt = captured["prompt"]
    assert result["analysis"] is not None
    assert result["grounded_authority_count"] == 0
    assert result["sections"]["your_rights"] == "Needs Georgia verification."
    assert "general legal information" in prompt
    assert "never create a citation" in prompt
    assert "###" not in result["analysis"] and "**" not in result["analysis"]
    assert result["coverage_notice"] is None


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