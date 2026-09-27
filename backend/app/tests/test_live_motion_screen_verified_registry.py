"""Release guard: the live motion-screen endpoint must use verified authority orchestration."""
from pathlib import Path

MAIN = Path(__file__).resolve().parents[1] / "main.py"


def test_live_motion_screen_uses_verified_registry_service():
    source = MAIN.read_text()
    assert "from .motion_screen_service import motion_screen_response" in source
    route = source.split("def private_motion_screen", 1)[1].split("@app.", 1)[0]
    # The live route must stay on the verified authority service. The AI callable
    # may be the public wrapper or the delegated wrapper used during incremental
    # endpoint migration, so guard the service call rather than one exact symbol.
    assert "motion_screen_response(db,facts," in route.replace(" ", "")
    assert "verification_mode" not in route  # response contract belongs to the service
    assert "prompt='GEORGIA CRIMINAL CASE MOTION SCREEN" not in route
    assert "RUN_MOTION_SCREEN" in route
    assert "temporarily unavailable" in route
