"""Static release guards for the approved Android navigation shell."""
from pathlib import Path


HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')
AUTH = Path('../android/app/src/main/java/help/galaw/standalone/AuthActivity.kt')


def test_home_preserves_approved_screen_and_back_navigation():
    source = HOME.read_text()
    assert 'ApprovedHomeScreen(this, homeActions).build()' in source
    assert 'override fun onBackPressed()' in source
    assert 'if (!onHome) showHome() else super.onBackPressed()' in source
    assert 'contentDescription = "Back to Home"' in source
    assert 'setOnClickListener { showHome() }' in source


def test_visible_home_actions_are_wired():
    source = HOME.read_text()
    expected = [
        'openCases() = showCases()',
        'openTalkToMe() = showTalkToMe()',
        'openLegalTools() = showLegalTools()',
        'openGeorgiaLaws() = showGeorgiaLaws()',
        'openCourtInfo() = showCourtInfo()',
        'openLegalForms() = showLegalForms()',
        'openCaseAnalysis() = showCaseAnalysis()',
        'openKnowYourRights() = showKnowYourRights()',
        'openResources() = showResources()',
        'openEmergency() = showEmergency()',
        'openDocuments() = showDocuments()',
    ]
    for action in expected:
        assert action in source


def test_async_errors_have_controlled_recovery():
    home = HOME.read_text()
    auth = AUTH.read_text()
    assert 'catch(e:Exception)' in home
    assert 'catch(e:Exception)' in auth
    assert 'Something went wrong. Please try again.' in home
    assert 'Something went wrong. Please try again.' in auth
