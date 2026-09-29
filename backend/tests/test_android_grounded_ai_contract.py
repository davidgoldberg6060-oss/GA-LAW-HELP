from pathlib import Path

API = Path('../android/app/src/main/java/help/galaw/standalone/ApiClient.kt')


def test_native_api_exposes_grounded_modes():
    source = API.read_text()
    assert 'fun groundedLegalAssistant' in source
    assert 'fun talkToMeAnalysis(transcript:String)=groundedLegalAssistant(transcript,"talk_to_me")' in source
    assert 'fun rightsAnalysis(description:String)=groundedLegalAssistant(description,"rights")' in source
    assert 'fun motionsAnalysis(facts:String)=groundedLegalAssistant(facts,"motions")' in source
    assert 'fun caseAnalysisWithVerifiedAuthorities(facts:String)=groundedLegalAssistant(facts,"case_analysis")' in source


def test_grounded_native_calls_use_internal_legal_assistant_endpoint():
    source = API.read_text()
    assert 'execute("/internal/legal-assistant","POST"' in source
    assert 'JSONObject().put("query",query).put("mode",mode)' in source
