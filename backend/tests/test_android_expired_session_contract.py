"""Release guard: Android opens without login; dead sessions fall back to the anonymous device identity."""
from pathlib import Path

API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')
HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')
MANIFEST = Path('../android/app/src/main/AndroidManifest.xml')


def test_failed_refresh_clears_dead_credentials_and_reauthenticates_anonymously():
    source = API.read_text()
    compact = ''.join(source.split())
    assert 'fun clearSession()' in source
    assert 'if(code==401&&retry&&refreshAccess())' in compact
    assert 'if(code==401&&!path.startsWith("/auth/")){expireSession();' in compact
    assert 'privatefunexpireSession(){clearSession();runCatching{anonymousSignIn()}}' in compact
    assert 'AuthActivity::class.java' not in source


def test_auth_endpoints_do_not_trigger_session_fallback():
    assert '!path.startsWith("/auth/")' in API.read_text()


def test_anonymous_device_key_is_random_encrypted_and_survives_sign_out():
    source = API.read_text()
    assert '"device_identity"' in source and 'SecureRandom' in source
    assert '"/auth/anonymous"' in source
    assert 'fun ensureSession()' in source


def test_app_launches_into_home_without_login():
    manifest = MANIFEST.read_text()
    home = manifest.split('android:name=".HomeActivity"', 1)[1].split('</activity>', 1)[0]
    assert 'android.intent.category.LAUNCHER' in home
    assert '<activity android:name=".AuthActivity" android:exported="false" />' in manifest
    compact = ''.join(HOME.read_text().split())
    assert 'privatefunrequireSignedIn():Boolean=true' in compact
    catalog = ''.join((HOME.parent / 'HomeDrawerCatalog.kt').read_text().split())
    assert ',true)' not in catalog
    assert 'HomeDrawerItem("funny",' in catalog
