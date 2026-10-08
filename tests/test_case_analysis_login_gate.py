from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_case_analysis_and_my_cases_stay_login_gated():
    screens = (ROOT / "src" / "ApprovedScreens.tsx").read_text()
    assert 'panel === "analysis"' in screens
    assert 'panel === "cases"' in screens
    assert "does not accept files" in screens
    assert "does not call the case API" in screens
    assert "Sign in before upload" in screens
    assert "Sign in to open My Cases" in screens
    assert "type=\"file\"" not in screens
    assert "/cases/" not in screens
    assert "authApi" not in screens
    assert "Do not resist" in screens or "SAFETY_NOTICE" in screens
