from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_guest_free_research_uses_public_rights_endpoints():
    app = (ROOT / "src" / "App.tsx").read_text()
    guest = (ROOT / "src" / "guestPublic.ts").read_text()
    docker = (ROOT / "Dockerfile.web").read_text()
    assert "guestRightsAndEncounter" in app
    assert "do not require sign-in" in app
    assert "motion screening, and defense analysis stay login-only" in app
    assert "rights guidance, police-encounter help, emergency guidance, cases, documents, recordings, motion screening and defense analysis require a paid membership" not in app
    assert "guestEncounterReply" in app
    assert "/public/rights-assistant" in guest
    assert "/public/encounter" in guest
    assert "guestOfficialIndexes" in guest
    assert "gasupreme.us" in guest
    assert "not a claim that any citation is current" in guest
    assert "indexedAuthorityLinks" in guest
    assert "not verified as current Georgia law" in guest
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


def test_motion_screen_uses_private_verified_endpoint():
    app = (ROOT / "src" / "App.tsx").read_text()
    assert "async function screenMotions()" in app
    assert "/motion-screen" in app
    assert "additional_facts" in app
    assert "verification_mode" in app
    assert "authApi('/public/ask'" not in app
    assert "Sign in to use the private case workspace." in app


def test_android_public_ask_does_not_use_login_only_assistant():
    client = (ROOT / "android/app/src/main/java/help/galaw/standalone/ApiClient.kt").read_text()
    assert "GuestPublicApi.rightsAssistant" in client
    assert "GuestPublicApi.encounter" in client
    assert 'groundedLegalAssistant(question, "talk_to_me")' not in client
