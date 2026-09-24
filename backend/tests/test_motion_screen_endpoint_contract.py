"""Regression guard for the live motion-screen endpoint contract.

The endpoint must delegate to the verified-registry service rather than maintaining
an independent free-form prompt path.
"""
from pathlib import Path


def test_live_motion_screen_uses_verified_response_service():
    source = (Path(__file__).parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    assert "from .motion_screen_service import motion_screen_response" in source

    route_start = source.index("def private_motion_screen(")
    route_end = source.index("\n@app.", route_start)
    route = source[route_start:route_end]

    assert "motion_screen_response(db, facts, ask_openai)" in route
    assert "GEORGIA CRIMINAL CASE MOTION SCREEN" not in route
    assert "audit(db,user.id,'RUN_MOTION_SCREEN','case',case_id)" in route
    assert "The motion screening assistant is temporarily unavailable." in route
