"""Release guard for expired Android sessions on protected screens."""
from pathlib import Path

API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')
HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')


def test_failed_refresh_clears_dead_credentials():
    source = API.read_text()
    assert 'fun clearSession()' in source
    compact = ''.join(source.split())
    assert 'if(code==401&&retry&&refreshAccess())' in compact
    assert 'if(code==401&&!path.startsWith("/auth/"))expireSession()' in compact


def test_expired_protected_session_redirects_to_login_and_finishes_activity():
    source = API.read_text()
    assert 'private fun expireSession()' in source
    assert 'clearSession()' in source
    assert 'AuthActivity::class.java' in source
    assert 'Intent.FLAG_ACTIVITY_CLEAR_TOP' in source
    assert 'activity.finish()' in source


def test_auth_endpoints_do_not_trigger_protected_session_redirect():
    source = API.read_text()
    assert '!path.startsWith("/auth/")' in source


def test_home_still_guards_missing_token_on_launch():
    source = HOME.read_text()
    assert 'if (api.token == null)' in source
    assert 'startActivity(Intent(this, AuthActivity::class.java))' in source
    assert 'finish()' in source
