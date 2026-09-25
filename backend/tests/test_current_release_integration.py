"""Cross-cutting release guards for the current production candidate."""
from pathlib import Path

MAIN = Path('app/main.py')
HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')
API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')


def test_live_motion_screen_uses_verified_service_and_audits():
    source = MAIN.read_text()
    assert 'from .motion_screen_service import motion_screen_response' in source
    assert "@app.post('/cases/{case_id}/motion-screen')" in source
    assert 'response=motion_screen_response(db, facts, ask_openai)' in source
    assert "HTTPException(503,'The motion screening assistant is temporarily unavailable.')" in source
    assert "audit(db,user.id,'RUN_MOTION_SCREEN','case',case_id);db.commit()" in source
    assert 'return response' in source


def test_approved_home_shell_and_back_navigation_remain_present():
    source = HOME.read_text()
    assert 'ApprovedHomeScreen(this, homeActions).build()' in source
    assert 'override fun onBackPressed()' in source
    assert 'if (!onHome) showHome() else super.onBackPressed()' in source


def test_expired_session_has_local_cleanup_and_login_redirect():
    api = API.read_text()
    home = HOME.read_text()
    assert 'clearSession' in api
    assert 'statusCode == 401' in home
    assert 'AuthActivity::class.java' in home
    assert 'finish()' in home
