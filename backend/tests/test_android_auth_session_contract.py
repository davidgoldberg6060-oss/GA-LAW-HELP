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
    compact = ''.join(source.split())
    assert 'if(code==401&&retry&&refreshAccess())returnexecute(path,method,body,false)' in compact
    assert 'funme()=JSONObject(execute("/me"))' in compact


def test_logout_revokes_refresh_token_then_clears_local_session():
    source = API.read_text()
    assert 'execute("/auth/logout","POST"' in ''.join(source.split())
    assert 'prefs.edit().clear().apply()' in source


def test_auth_entry_does_not_open_protected_app_without_token():
    source = AUTH.read_text()
    assert 'if (api.token != null) openApp() else showAuth()' in source
    assert 'if(validateLogin(emailValue,passwordValue)) runTask("Signing in…")' in source


def test_verification_and_reset_paths_validate_required_input():
    source = AUTH.read_text()
    assert 'tokenValue.isBlank()' in source
    assert 'passwordValue.length < 15' in source
    assert 'if(!validEmail(value))' in source
    assert 'If the account exists, a reset email was sent.' in source


def test_login_accepts_existing_short_passwords_but_signup_and_reset_keep_policy():
    """Existing accounts may have passwords under 15 characters (backend Login has no length
    rule); only registration and reset enforce the backend 15-128 policy."""
    source = AUTH.read_text()
    login = source.split('private fun validateLogin(', 1)[1].split('return true', 1)[0]
    assert 'password.isEmpty()' in login
    assert 'length < 15' not in login and '128' not in login
    registration = source.split('private fun validateRegistration(', 1)[1].split('private fun ', 1)[0]
    assert 'password.length < 15' in registration
    assert 'password.length > 128' in registration
    assert 'if(validateRegistration(emailValue,passwordValue)) runTask("Creating account…")' in source
    assert 'passwordValue.length > 128' in source
    assert 'validateCredentials' not in source
    schemas = Path('app/schemas.py').read_text()
    login_schema = schemas.split('class Login(BaseModel):', 1)[1].split('class ', 1)[0]
    assert 'min_length' not in login_schema
    assert 'password: str = Field(min_length=15, max_length=128)' in schemas
