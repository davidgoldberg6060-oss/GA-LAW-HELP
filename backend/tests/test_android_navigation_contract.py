"""Static release guards for the approved Android navigation shell."""
from pathlib import Path


HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')
AUTH = Path('../android/app/src/main/java/help/galaw/standalone/AuthActivity.kt')


def test_home_preserves_approved_screen_and_back_navigation():
    source = HOME.read_text()
    compact = ''.join(source.split())
    assert 'ApprovedHomeScreen(this,homeActions).build()' in compact
    assert 'override fun onBackPressed()' in source
    assert 'if(!onHome)showHome()elsesuper.onBackPressed()' in compact
    assert 'contentDescription="BacktoHome"' in compact
    assert 'setOnClickListener{showHome()}' in compact


def test_visible_home_actions_are_wired():
    source = HOME.read_text()
    expected = [
        'openCases() = showCases()',
        'openTalkToMe() = showTalkToMe()',
        'openLegalTools() = showLegalTools()',
        'openGeorgiaLaws() = showGeorgiaLaws()',
        'openCourtInfo() = showCourtInfo()',
        'openLegalForms() = showLegalForms()',
        'openCaseAnalysis() = showMyCase()',  # Case Analysis tile opens the My Case hub
        'openKnowYourRights() = showKnowYourRights()',
        'openResources() = showResources()',
        'openEmergency() = showEmergency()',
        'openDocuments() = showDocuments()',
    ]
    compact = ''.join(source.split())
    for action in expected:
        assert ''.join(action.split()) in compact


def test_async_errors_have_controlled_recovery():
    home = HOME.read_text()
    auth = AUTH.read_text()
    assert 'catch(e:Exception)' in home
    assert 'catch(e:Exception)' in auth
    assert 'Something went wrong. Please try again.' in home
    assert 'Something went wrong. Please try again.' in auth
