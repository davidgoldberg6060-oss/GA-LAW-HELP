import re
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


def test_home_guards_private_screens_when_token_is_missing():
    """HomeActivity opens without a session so free guest rights research is reachable
    (PR #119, docs/GUEST_PUBLIC_RIGHTS.md). The launch-time missing-token redirect was
    replaced by requireSignedIn(), which must still send token-less users to login before
    any private screen (cases, documents, legal tools, case analysis, account) loads.
    """
    source = HOME.read_text()
    compact = ''.join(source.split())
    assert 'privatefunrequireSignedIn():Boolean{if(api.token!=null)returntrue;' in compact
    assert 'startActivity(Intent(this,AuthActivity::class.java));returnfalse}' in compact
    for screen in ('showCases', 'showDocuments', 'showLegalTools', 'showCaseAnalysis', 'showAccount'):
        assert f'privatefun{screen}(){{if(!requireSignedIn())return;' in compact, screen
    # The drawer is now driven by HomeDrawerCatalog: private items carry requiresSignIn and the
    # side-drawer handler (onDrawerItem) checks it before dispatching (each private screen also guards itself above).
    assert 'privatefunonDrawerItem(item:HomeDrawerItem){if(item.requiresSignIn&&!requireSignedIn())return;' in compact
    assert 'privatefunshowMotionsHub(){if(!requireSignedIn())return;' in compact
    catalog = ''.join((HOME.parent / 'HomeDrawerCatalog.kt').read_text().split())
    for item_id in ('cases', 'motions', 'profile'):
        assert re.search(rf'HomeDrawerItem\("{item_id}","[^"]+",true\)', catalog), item_id
    assert 'finish()' in source
