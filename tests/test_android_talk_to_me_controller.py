from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "android/app/src/main/java/help/galaw/standalone/TalkToMeController.kt"
MAIN = ROOT / "android/app/src/main/java/help/galaw/standalone/MainActivity.kt"


def test_controller_uses_grounded_conversation_only():
    text = CONTROLLER.read_text(encoding="utf-8")
    assert "GroundedConversation.analyze" in text
    assert "publicAsk(" not in text
    assert "groundedLegalAssistant(" not in text
    assert "talkToMeAnalysis(" not in text


def test_controller_preserves_authority_summary_in_transcript():
    text = CONTROLLER.read_text(encoding="utf-8")
    assert "turn.transcriptEntry" in text
    assert "turn.authoritySummary" in text
    assert "history.append(reply.transcriptEntry)" in text


def test_legacy_activity_call_is_visible_until_final_ui_wiring():
    # Deliberately documents the remaining release task instead of pretending it is complete.
    # Remove this assertion when MainActivity is switched to TalkToMeController.reply().
    text = MAIN.read_text(encoding="utf-8")
    assert "api.publicAsk(prompt)" in text
