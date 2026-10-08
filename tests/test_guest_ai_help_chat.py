from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ai_help_chat_stays_on_public_rights_assistant():
    screens = (ROOT / "src" / "ApprovedScreens.tsx").read_text()
    app = (ROOT / "src" / "App.tsx").read_text()
    assert "sendGuestChat" in screens
    assert "/public/rights-assistant" in screens
    assert "does not read My Cases" in screens
    assert "Do not resist" in screens or "SAFETY_NOTICE" in screens
    assert "askGuest" in app
    assert "guestRightsAndEncounter" in app
    assert "/cases/" not in screens
    assert "authApi" not in screens
