"""Release guard for wiring the live motion-screen route to the verified registry service."""
from pathlib import Path


def test_live_motion_route_uses_verified_motion_response():
    source = Path('app/main.py').read_text()
    route_marker = "@app.post('/cases/{case_id}/motion-screen')"
    assert route_marker in source
    route = source.split(route_marker, 1)[1].split("@app.", 1)[0]
    assert 'motion_screen_response' in source
    assert 'motion_screen_response(db, facts, ask_openai)' in route
    assert "HTTPException(503" in route
    assert "RUN_MOTION_SCREEN" in route
