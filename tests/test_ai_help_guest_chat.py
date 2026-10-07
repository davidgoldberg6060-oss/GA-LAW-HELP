from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ai_help_chat_stays_on_guest_rights_path():
    screen = (ROOT / "src" / "ApprovedScreens.tsx").read_text()
    css = (ROOT / "src" / "approvedScreens.css").read_text()
    assert "AI Help" in screen
    assert "approvedChat" in screen
    assert "/public/rights-assistant" in screen
    assert "does not invent statute or case text" in screen
    assert "props.onAsk(text)" in screen
    assert "Do not resist, run, or lie" in screen
    assert "Lexis" not in screen or "No Lexis editor notes" in screen
    assert "O.C.G.A." not in screen
    assert "authApi" not in screen
    assert ".approvedChat .user" in css
    assert "#e2b54e" in css
    assert "#02111d" in css
