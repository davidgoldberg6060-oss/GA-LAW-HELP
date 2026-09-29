from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONVERSATION = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedConversation.kt"
API = ROOT / "android/app/src/main/java/help/galaw/standalone/ApiClient.kt"
RENDERER = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedLegalResult.kt"


def test_talk_to_me_adapter_uses_dedicated_grounded_endpoint():
    conversation = CONVERSATION.read_text(encoding="utf-8")
    api = API.read_text(encoding="utf-8")
    assert "api.talkToMeAnalysis(request)" in conversation
    assert "fun talkToMeAnalysis" in api
    assert 'legalAssistant(query,"talk_to_me")' in api


def test_conversation_context_is_bounded_and_requires_a_message():
    source = CONVERSATION.read_text(encoding="utf-8")
    assert "MAX_CONTEXT_CHARS = 12_000" in source
    assert "takeLast(MAX_CONTEXT_CHARS)" in source
    assert 'require(cleanMessage.isNotEmpty())' in source


def test_conversation_explicitly_blocks_fabricated_authority():
    source = CONVERSATION.read_text(encoding="utf-8")
    assert "Use only the verified authorities supplied" in source
    assert "instead of inventing a statute, case, holding, citation, deadline, or procedural rule" in source


def test_conversation_renders_backend_authority_metadata_without_upgrading_it():
    conversation = CONVERSATION.read_text(encoding="utf-8")
    renderer = RENDERER.read_text(encoding="utf-8")
    assert "GroundedLegalResult.answer(result)" in conversation
    assert "GroundedLegalResult.authoritySummary(result)" in conversation
    assert 'optBoolean("usable_as_support",false)' in renderer
    assert "RESEARCH ONLY — not usable as supporting authority" in renderer
