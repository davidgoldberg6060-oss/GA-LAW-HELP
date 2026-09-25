"""Release guard for expired Android sessions on protected screens."""
from pathlib import Path

API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')
HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')


def test_failed_refresh_clears_dead_credentials():
    source = API.read_text()
    assert 'clearSession' in source, 'ApiClient must expose a local session-clear operation.'
    assert 'code == 401' in source


def test_protected_screen_redirects_unauthorized_user_to_login():
    source = HOME.read_text()
    assert 'ApiException' in source
    assert 'statusCode == 401' in source
    assert 'AuthActivity::class.java' in source
    assert 'finish()' in source


def test_home_still_guards_missing_token_on_launch():
    source = HOME.read_text()
    assert 'if (api.token == null)' in source
    assert 'startActivity(Intent(this, AuthActivity::class.java))' in source
