from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vite_rewrite_targets_public_guest_endpoints():
    config = (ROOT / "vite.config.ts").read_text()
    assert "guestRightsAndEncounter" in config
    assert "guestEncounterReply" in config
    assert "/public/rights-assistant" in (ROOT / "src" / "guestPublic.ts").read_text()
    assert "/public/encounter" in (ROOT / "src" / "guestPublic.ts").read_text()
    assert "authApi('/cases'" in (ROOT / "src" / "App.tsx").read_text() or "/cases/" in (ROOT / "src" / "App.tsx").read_text()


def test_private_case_workspace_still_requires_session_helper():
    app = (ROOT / "src" / "App.tsx").read_text()
    assert "Sign in to use the private case workspace." in app
    assert "openCaseWorkspace" in app
