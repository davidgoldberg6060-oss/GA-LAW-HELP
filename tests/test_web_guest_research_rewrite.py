from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_guest_free_research_uses_public_rights_endpoints():
    app = (ROOT / "src" / "App.tsx").read_text()
    guest = (ROOT / "src" / "guestPublic.ts").read_text()
    docker = (ROOT / "Dockerfile.web").read_text()
    assert "guestRightsAndEncounter" in app
    assert "guestEncounterReply" in app
    assert "/public/rights-assistant" in guest
    assert "/public/encounter" in guest
    assert "Authorization" not in guest
    assert "Create a free account or sign in to use AI legal research." not in app
    assert "authApi('/public/ask'" not in app
    assert "function openPolice(){setTool('police')}" in app
    assert "function openRights(next:ScenarioKey=scenario){setScenario(next);setTool('avoid')}" in app
    assert "vite.config.ts" in docker
    # Private case tools stay login-only.
    assert "Sign in to use the private case workspace." in app
    assert "function authApi" in app
    assert "authApi('/cases'" in app or "/cases/" in app


def test_android_public_ask_does_not_use_login_only_assistant():
    client = (ROOT / "android/app/src/main/java/help/galaw/standalone/ApiClient.kt").read_text()
    assert "GuestPublicApi.rightsAssistant" in client
    assert "GuestPublicApi.encounter" in client
    assert 'groundedLegalAssistant(question, "talk_to_me")' not in client
