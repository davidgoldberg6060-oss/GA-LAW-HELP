from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_case_panels_stay_login_only_and_off_guest_rights():
    screens = (ROOT / "src" / "ApprovedScreens.tsx").read_text()
    assert 'panel === "cases"' in screens
    assert 'panel === "analysis"' in screens
    assert "Private case lists stay login-only" in screens
    assert "Guest research cannot receive a case file" in screens
    assert "/public/rights-assistant" in screens
    assert "/cases/" not in screens
    assert "authApi" not in screens
    assert "Do not resist" in screens or "SAFETY_NOTICE" in screens
