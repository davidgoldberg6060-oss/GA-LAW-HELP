from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONVERSATION = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedConversation.kt"
MODE = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedLegalMode.kt"
API = ROOT / "android/app/src/main/java/help/galaw/standalone/ApiClient.kt"
RENDERER = ROOT / "android/app/src/main/java/help/galaw/standalone/GroundedLegalResult.kt"


def test_talk_to_me_adapter_uses_public_guest_endpoints():
    conversation = CONVERSATION.read_text(encoding="utf-8")
    mode = MODE.read_text(encoding="utf-8")
    api = API.read_text(encoding="utf-8")
    assert "GroundedLegalMode.analyze(api, GroundedLegalMode.Mode.TALK_TO_ME, request)" in conversation
    assert 'Mode.TALK_TO_ME -> guestRightsAndEncounter(clean, "talk_to_me")' in mode
    assert "GuestPublicApi.encounter(BuildConfig.API_BASE_URL, query)" in mode
    assert "GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, query, mode)" in mode
    assert "api.talkToMeAnalysis(" not in mode
    # Private case analysis still has a login-only client method. Guest talk-to-me must not use it.
    assert "fun talkToMeAnalysis" in api
    assert 'execute("/internal/legal-assistant"' in api


def test_conversation_context_is_bounded_and_requires_a_message():
    source = CONVERSATION.read_text(encoding="utf-8")
    assert "MAX_CONTEXT_CHARS = 12_000" in source
    assert "takeLast(MAX_CONTEXT_CHARS)" in source
    assert "require(cleanMessage.isNotEmpty())" in source


def test_conversation_explicitly_blocks_fabricated_authority():
    source = CONVERSATION.read_text(encoding="utf-8")
    assert "Use only the verified authorities supplied" in source
    assert "instead of inventing a statute, case, holding, citation, deadline, or procedural rule" in source


def test_conversation_renders_backend_authority_metadata_without_upgrading_it():
    conversation = CONVERSATION.read_text(encoding="utf-8")
    mode = MODE.read_text(encoding="utf-8")
    renderer = RENDERER.read_text(encoding="utf-8")
    assert "GroundedLegalMode.analyze(" in conversation
    assert "GroundedLegalResult.answer(raw)" in mode
    assert "GroundedLegalResult.authoritySummary(raw)" in mode
    assert 'optBoolean("usable_as_support", true).not()' in renderer
    assert "Research only \u2014 not used as supporting authority." in renderer
