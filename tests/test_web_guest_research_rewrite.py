from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vite_rewrite_targets_public_guest_endpoints():
    config = (ROOT / "vite.config.ts").read_text()
    app = (ROOT / "src" / "App.tsx").read_text()
    guest = (ROOT / "src" / "guestPublic.ts").read_text()
    assert "guestRightsAndEncounter" in config
    assert "guestEncounterReply" in config
    assert "/public/rights-assistant" in guest
    assert "/public/encounter" in guest
    assert "Authorization" not in guest
    assert "authApi('/cases'" in app or "/cases/" in app
    # The compile-time rewrite only works if these source strings still exist.
    assert "Create a free account or sign in to use AI legal research." in app
    assert "authApi('/public/ask'" in app
    assert "authApi('/public/research?q='" in config or "authApi('/public/research?q='" in app
    assert "function openPolice(){if(!user)" in app
    assert "if(!paid){setPaywallOpen(true);return}setTool('avoid')" in app


def test_private_case_workspace_still_requires_session_helper():
    app = (ROOT / "src" / "App.tsx").read_text()
    assert "Sign in to use the private case workspace." in app
    assert "openCaseWorkspace" in app
    assert "function authApi" in app
