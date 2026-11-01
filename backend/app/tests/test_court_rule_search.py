from app.authority_search_service import PUBLIC_LAW_KINDS, build_query_plan, rule_citations


def test_rule_citation_patterns():
    assert rule_citations("Unif. Mag. Ct. R. 5") == ["Unif. Mag. Ct. R. 5"]
    assert rule_citations("Ga. Sup. Ct. R. 22") == ["Ga. Sup. Ct. R. 22"]
    assert rule_citations("Uniform Superior Court Rule 6.4") == ["Unif. Super. Ct. R. 6.4"]
    assert rule_citations("court of appeals rule 40") == ["Ga. Ct. App. R. 40"]
    assert rule_citations("superior court 5 days") == []
    assert rule_citations("O.C.G.A. 16-5-20") == []


def test_plan_pins_rules_and_small_claims():
    assert "Unif. Mag. Ct. R. 5" in build_query_plan("Unif. Mag. Ct. R. 5").pinned_citations
    plan = build_query_plan("how do I file a small claims case in Georgia")
    assert "magistrate" in plan.expansion_terms
    assert "Unif. Mag. Ct. R. 17" in plan.pinned_citations
    assert "O.C.G.A. § 15-10-43" in plan.pinned_citations


def test_law_search_includes_court_rules():
    assert "court_rule" in PUBLIC_LAW_KINDS["statutes"]
