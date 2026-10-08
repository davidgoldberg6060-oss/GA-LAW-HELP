from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_my_cases_list_stays_login_only():
    screens = (ROOT / "src" / "ApprovedScreens.tsx").read_text()
    app = (ROOT / "src" / "App.tsx").read_text()
    assert "My Cases" in screens
    assert "Private cases stay login-only" in screens
    assert "does not invent matters" in screens
    assert "Case Analysis" in screens
    assert "does not send a file to guest research" in screens
    assert "cases={cases.map" in app
    assert "/public/rights-assistant" in screens
    assert "authApi" not in screens
    assert "/cases/" not in screens
