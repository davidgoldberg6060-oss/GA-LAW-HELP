"""Web free research must not demand login. Private motion screening must."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _slice(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def test_web_free_research_uses_public_guest_endpoints():
    app = (ROOT / "src/App.tsx").read_text(encoding="utf-8")
    guest = (ROOT / "src/guestPublic.ts").read_text(encoding="utf-8")
    research = _slice(app, "async function runResearch", "async function startCamera")
    encounter = _slice(app, "async function getEncounterAI", "async function submitAuth")
    assert "guestRightsAndEncounter" in research
    assert "setAuthOpen" not in research
    assert "authApi" not in research
    assert "guestEncounterReply" in encounter
    assert "authApi" not in encounter
    assert "'/public/rights-assistant'" in guest
    assert "'/public/encounter?situation='" in guest
    assert "not a claim that any citation is current" in guest


def test_web_private_motion_screen_stays_login_only():
    app = (ROOT / "src/App.tsx").read_text(encoding="utf-8")
    motions = _slice(app, "async function screenMotions", "async function checkActiveCaseMotions")
    case_motions = _slice(app, "async function checkActiveCaseMotions", "async function checkDefenseStrategy")
    assert "if(!user)" in motions
    assert "Sign in to use the private case workspace." in motions
    assert "authApi('/cases/'+id+'/motion-screen'" in motions
    assert "authApi('/cases/'+id+'/motion-screen'" in case_motions
    assert "guestRightsAndEncounter" not in motions
