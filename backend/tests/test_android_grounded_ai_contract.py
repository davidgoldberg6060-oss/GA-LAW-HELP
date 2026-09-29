from pathlib import Path

API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')
HOME = Path('../android/app/src/main/java/help/galaw/standalone/HomeActivity.kt')


def test_native_api_exposes_grounded_modes():
    source = API.read_text()
    assert 'fun groundedLegalAssistant' in source
    assert 'fun talkToMeAnalysis(transcript:String)=groundedLegalAssistant(transcript,"talk_to_me")' in source
    assert 'fun rightsAnalysis(description:String)=groundedLegalAssistant(description,"rights")' in source
    assert 'fun motionsAnalysis(facts:String)=groundedLegalAssistant(facts,"motions")' in source
    assert 'fun caseAnalysisWithVerifiedAuthorities(facts:String)=groundedLegalAssistant(facts,"case_analysis")' in source


def test_talk_to_me_screen_must_not_fall_back_to_ungrounded_public_ask():
    source = HOME.read_text()
    start = source.index('private fun showTalkToMe()')
    end = source.index('private fun showCases()', start)
    talk = source[start:end]
    assert 'api.talkToMeAnalysis(q)' in talk
    assert 'api.publicAsk(q)' not in talk
