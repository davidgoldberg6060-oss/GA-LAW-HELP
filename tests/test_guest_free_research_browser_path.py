"""Issue 82 guest path: Free research must not open an account dialog.

This is a source-level browser-path contract. It does not claim the legal corpus
is complete or that any citation is current Georgia law.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _slice(text: str, start_marker: str, end_marker: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start + len(start_marker))
    return text[start:end]


def test_free_research_button_does_not_demand_login():
    app = (ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    guest = (ROOT / "src" / "guestPublic.ts").read_text(encoding="utf-8")
    assert "Free research" in app
    assert "onClick={()=>runResearch()}" in app or "onSubmit={runResearch}" in app
    research = _slice(app, "async function runResearch", "async function startCamera")
    assert "guestRightsAndEncounter(API,api,q.trim())" in research
    assert "setAuthOpen(true)" not in research
    assert "setMode('register')" not in research
    assert "Create a free account or sign in to use AI legal research." not in app
    assert "POST /public/rights-assistant" not in research  # called inside guestPublic
    assert "/public/rights-assistant" in guest
    assert "/public/encounter" in guest
    assert "Authorization" not in guest


def test_private_case_workspace_still_requires_login():
    app = (ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    workspace = _slice(app, "async function openCaseWorkspace", "async function selectCase")
    assert "setAuthOpen(true)" in workspace
    assert "private case tools" in workspace
    motions = _slice(app, "async function screenMotions", "async function analyzeCase")
    assert "Sign in to use the private case workspace." in motions
    assert "/motion-screen" in motions
    assert "authApi(" in motions
