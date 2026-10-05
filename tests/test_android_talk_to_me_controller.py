from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "android/app/src/main/java/help/galaw/standalone/TalkToMeController.kt"
MAIN = ROOT / "android/app/src/main/java/help/galaw/standalone/MainActivity.kt"


def test_controller_uses_grounded_conversation_only():
    text = CONTROLLER.read_text(encoding="utf-8")
    assert "GroundedConversation.analyze" in text
    assert "GuestPublicApi.encounter" in text
    assert "publicAsk(" not in text
    assert "groundedLegalAssistant(" not in text
    assert "talkToMeAnalysis(" not in text


def test_controller_preserves_authority_summary_in_transcript():
    text = CONTROLLER.read_text(encoding="utf-8")
    assert "turn.transcriptEntry" in text
    assert "turn.authoritySummary" in text
    assert "history.append(reply.transcriptEntry)" in text


def test_main_talk_to_me_uses_guest_controller_not_rights_public_ask():
    text = MAIN.read_text(encoding="utf-8")
    start = text.index("private fun showTalkToMe()")
    end = text.index("private fun showTalkSaveCase", start)
    screen = text[start:end]
    assert "TalkToMeController.reply" in screen
    assert "TalkToMeController.append" in screen
    assert "api.publicAsk(" not in screen
    assert "requirePaid{showTalkToMe()" not in text
