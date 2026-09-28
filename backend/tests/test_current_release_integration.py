"""Cross-cutting release guards for the current production candidate."""
from pathlib import Path

MAIN = Path('app/main.py')
HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')
API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')
WEB = Path('../src/App.tsx')


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
    assert 'ApprovedHomeScreen(this,homeActions).build()' in ''.join(source.split())
    assert 'override fun onBackPressed()' in source
    assert 'if(!onHome)showHome()elsesuper.onBackPressed()' in ''.join(source.split())


def test_expired_session_has_local_cleanup_and_login_redirect():
    api = API.read_text()
    home = HOME.read_text()
    assert 'clearSession' in api
    assert 'if(code==401&&!path.startsWith("/auth/"))expireSession()' in ''.join(api.split())
    assert 'AuthActivity::class.java' in home
    assert 'finish()' in home


def test_free_launch_web_gate_is_disabled_but_billing_code_remains():
    source = WEB.read_text()
    assert 'const FREE_LAUNCH=true;' in source
    assert 'const paid=FREE_LAUNCH||' in source
    assert "'Free research'" in source
    assert '!FREE_LAUNCH&&paywallOpen' in source
    assert 'startCheckout' in source
    assert 'Create a free account or sign in to use AI legal research.' in source
