from datetime import date
from app.intelligence.case_engine import AuthorityHit, authority_applies, CaseFinding, FindingStatus, red_team
from app.intelligence.retrieval import SearchDocument, search
from app.intelligence.second_look import SecondLookInput, screen

def test_historical_authority_filter():
    h=AuthorityHit("1","123 Ga. 1","Test","Ga.",date(2020,1,1),None,"current","https://example.test","x")
    assert not authority_applies(h,date(2019,1,1))
    assert authority_applies(h,date(2021,1,1))

def test_retrieval_prioritizes_verified():
    docs=[SearchDocument("1","A","Search warrant","search warrant probable cause",True,"current"),SearchDocument("2","B","Other","search warrant",False,"unknown")]
    assert search("search warrant probable cause",docs)[0].document.id=="1"

def test_red_team_flags_missing_authority():
    f=CaseFinding("suppression",FindingStatus.POTENTIAL,"Possible issue",missing_facts=["warrant"],confidence=.4)
    assert len(red_team(f)["weaknesses"]) >= 2

def test_second_look_screen():
    out=screen(SecondLookInput("possible illegal sentence and merger","plea",True,False,[]))
    assert any(x["issue"]=="merger" and x["status"]=="potential_issue" for x in out)
