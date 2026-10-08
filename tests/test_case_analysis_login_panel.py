from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_case_analysis_panel_stays_login_only():
    screens = (ROOT / "src" / "ApprovedScreens.tsx").read_text()
    catalog = (ROOT / "src" / "approvedScreenCatalog.ts").read_text()
    assert 'panel === "analysis"' in screens
    assert "openPrivateAnalysis" in screens
    assert "Sign in required" in screens
    assert "does not invent unannotated code text" in screens
    assert "DATABASE_URL" in screens
    assert "type=\"file\"" not in screens
    assert "/public/rights-assistant" in screens
    assert "/cases/" not in screens
    assert "Case Analysis" in catalog
    assert "requiresSignIn: true" in catalog
