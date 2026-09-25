"""Release guards for Android authentication/session handling."""
from pathlib import Path

API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')
AUTH = Path('../android/app/src/main/java/help/galaw/standalone/AuthActivity.kt')


def test_tokens_are_kept_in_encrypted_preferences():
    source = API.read_text()
    assert 'EncryptedSharedPreferences.create' in source
    assert 'MasterKey.KeyScheme.AES256_GCM' in source
    assert '"access_token"' in source
    assert '"refresh_token"' in source


def test_unauthorized_request_refreshes_once_only():
    source = API.read_text()
    assert 'if (code == 401 && retry && refreshAccess()) return execute(path, method, body, false)' in source
    assert 'fun me(): JSONObject = JSONObject(execute("/me"))' in source


def test_logout_revokes_refresh_token_then_clears_local_session():
    source = API.read_text()
    assert 'execute("/auth/logout", "POST"' in source
    assert 'prefs.edit().clear().apply()' in source


def test_auth_entry_does_not_open_protected_app_without_token():
    source = AUTH.read_text()
    assert 'if (api.token != null) openApp() else showAuth()' in source
    assert 'if(validateCredentials(emailValue,passwordValue))' in source


def test_verification_and_reset_paths_validate_required_input():
    source = AUTH.read_text()
    assert 'tokenValue.isBlank()' in source
    assert 'passwordValue.length < 15' in source
    assert 'if(!validEmail(value))' in source
    assert 'If the account exists, a reset email was sent.' in source
