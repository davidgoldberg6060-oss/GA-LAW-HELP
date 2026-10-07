"""Approved navy/gold home tiles. Source contract only; no corpus is written."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_home_tiles_include_emergency_once_in_the_drawer():
    catalog = (ROOT / "src" / "approvedScreenCatalog.ts").read_text(encoding="utf-8")
    screens = (ROOT / "src" / "ApprovedScreens.tsx").read_text(encoding="utf-8")
    for label in (
        "My Cases",
        "AI Help",
        "Legal Tools",
        "Georgia Laws",
        "Court Info",
        "Legal Forms",
        "Case Analysis",
        "Know Your Rights",
        "Resources",
        "Emergency Help",
    ):
        assert label in catalog
    assert catalog.count('{ id: "emergency"') == 1
    assert "Dark Mode" in catalog and "Settings" in catalog and "Log Out" in catalog
    assert "requiresSignIn: true" in catalog
    assert "/public/rights-assistant" in catalog
    assert "Do not resist" in catalog
    assert "do not lie" in catalog.lower() or "Do not lie" in catalog
    assert "Lexis" in screens
    assert "approvedChat" in screens
    assert "onCases" in screens
