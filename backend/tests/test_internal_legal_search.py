import json

from app import internal_legal_search as legal_search


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _empty_supporting_corpora(tmp_path):
    _write(tmp_path / "georgia_court_of_appeals.jsonl", [])
    _write(tmp_path / "georgia_statutes.jsonl", [])
    _write(tmp_path / "georgia_rules_motions.jsonl", [])
    _write(tmp_path / "law_enforcement_authorities.jsonl", [])


def _fixture_corpus(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    _write(tmp_path / "georgia_supreme_opinions.jsonl", [{"title":"Example v. State","citation":"123 Ga. 456","court":"Supreme Court of Georgia","text":"search and seizure warrant probable cause","source_url":"https://example.invalid/case","verification_status":"verified"}])
    _write(tmp_path / "georgia_court_of_appeals.jsonl", [])
    _write(tmp_path / "georgia_statutes.jsonl", [{"heading":"Burglary statute","section_number":"O.C.G.A. § 16-7-1","text":"burglary elements dwelling","citation":"O.C.G.A. § 16-7-1","verification_status":"verified"}])
    _write(tmp_path / "georgia_rules_motions.jsonl", [{"heading":"Motion to suppress","rule_text":"motion to suppress unlawfully seized evidence","verification_status":"verified"}])
    _write(tmp_path / "law_enforcement_authorities.jsonl", [{"topic":"Traffic stop rights","authority_text":"traffic stop detention reasonable suspicion","verification_status":"verified"}])


def test_empty_query_returns_no_authority(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("   ")
    assert result["hits"] == []
    assert "Enter facts" in result["coverage_notice"]


def test_stop_words_only_query_returns_no_authority(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("what is the law for me", "case_analysis")
    assert result["hits"] == []
    assert "specific legal facts" in result["coverage_notice"]


def test_case_lookup_routes_only_cases_and_statutes(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("burglary", "case_lookup")
    assert result["hits"]
    assert {hit["corpus"] for hit in result["hits"]} <= {"cases", "statutes"}
    assert any(hit["citation"] == "O.C.G.A. § 16-7-1" for hit in result["hits"])


def test_case_lookup_exact_section_preserves_native_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    _write(tmp_path / "georgia_supreme_opinions.jsonl", [])
    _write(tmp_path / "georgia_court_of_appeals.jsonl", [])
    _write(tmp_path / "georgia_statutes.jsonl", [{"heading":"Sample Georgia statute","section_number":"O.C.G.A. § 16-8-2","citation":"O.C.G.A. § 16-8-2","text":"Sample theft statute text for retrieval testing only.","source_url":"https://example.gov/statute","verification_status":"verified","effective_date":"2026-01-01","jurisdiction":"Georgia"}])
    _write(tmp_path / "georgia_rules_motions.jsonl", [])
    _write(tmp_path / "law_enforcement_authorities.jsonl", [])
    result=legal_search.search_internal("16-8-2", "case_lookup")
    assert result["hits"]
    hit=result["hits"][0]
    assert hit["record_type"] == "statute"
    assert hit["section_number"] == "O.C.G.A. § 16-8-2"
    assert hit["effective_date"] == "2026-01-01"
    assert hit["jurisdiction"] == "Georgia"
    assert hit["verification_status"] == "verified"


def test_ocga_format_variants_resolve_same_statute(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    for query in ("O.C.G.A. § 16-7-1", "OCGA 16-7-1", "16-7-1"):
        result=legal_search.search_internal(query, "case_lookup")
        assert result["hits"]
        assert result["hits"][0]["citation"] == "O.C.G.A. § 16-7-1"


def test_case_lookup_exact_docket_number_prioritizes_matching_case(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    _write(tmp_path / "georgia_supreme_opinions.jsonl", [
        {"title":"Different v. State","citation":"320 Ga. 10","docket_number":"S26A0001","text":"appeal criminal judgment","verification_status":"verified"},
        {"title":"Target v. State","citation":"321 Ga. 20","docket_number":"S26A0421","text":"appeal criminal judgment","verification_status":"verified"},
    ])
    _empty_supporting_corpora(tmp_path)
    result=legal_search.search_internal("S26A0421", "case_lookup")
    assert result["hits"]
    assert result["hits"][0]["title"] == "Target v. State"
    assert result["hits"][0]["docket_number"] == "S26A0421"


def test_case_lookup_exact_case_number_prioritizes_matching_case(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    _write(tmp_path / "georgia_supreme_opinions.jsonl", [
        {"title":"First v. State","citation":"320 Ga. 11","case_number":"A26A0100","text":"criminal appeal","verification_status":"verified"},
        {"title":"Second v. State","citation":"320 Ga. 12","case_number":"A26A0999","text":"criminal appeal","verification_status":"verified"},
    ])
    _empty_supporting_corpora(tmp_path)
    result=legal_search.search_internal("A26A0999", "case_lookup")
    assert result["hits"]
    assert result["hits"][0]["title"] == "Second v. State"
    assert result["hits"][0]["case_number"] == "A26A0999"


def test_missing_legal_status_is_preserved_as_unknown_not_invented(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    _write(tmp_path / "georgia_supreme_opinions.jsonl", [{"title":"Status Test v. State","citation":"321 Ga. 1","text":"probable cause","source_url":"https://example.gov/case","verification_status":"verified"}])
    _empty_supporting_corpora(tmp_path)
    hit=legal_search.search_internal("probable cause", "case_lookup")["hits"][0]
    assert hit["currency_status"] == "unknown"
    assert hit["precedential_status"] == "unknown"
    assert hit["status_checked_at"] is None
    assert hit["status_source_url"] is None
    assert hit["negative_treatment"] == []


def test_rights_mode_can_retrieve_law_enforcement_authority(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("traffic stop reasonable suspicion", "rights")
    assert result["hits"][0]["corpus"] == "law_enforcement"


def test_motions_mode_can_retrieve_motion_authority(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("motion suppress seized evidence", "motions")
    assert result["hits"][0]["corpus"] == "motions_rules"


def test_unknown_terms_do_not_fabricate_results(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("zyxwvutsrqponmlkjihgfedcba", "case_analysis")
    assert result["hits"] == []
    assert "not invented" in result["coverage_notice"]


def test_long_question_rejects_single_weak_token_match(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("burglary probation sentence firearm appeal", "case_analysis")
    assert result["hits"] == []


def test_verified_authority_outranks_equivalent_unverified_authority(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    _write(tmp_path / "georgia_supreme_opinions.jsonl", [{"title":"Unverified Search Case","text":"probable cause search warrant","citation":"1 Ga. 1"},{"title":"Verified Search Case","text":"probable cause search warrant","citation":"2 Ga. 2","verification_status":"verified"}])
    _empty_supporting_corpora(tmp_path)
    result = legal_search.search_internal("probable cause search warrant", "case_analysis")
    assert result["hits"][0]["title"] == "Verified Search Case"
    assert result["hits"][0]["verification_status"] == "verified"
    assert result["hits"][1]["verification_status"] == "unverified"


def test_source_urls_must_be_https(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    _write(tmp_path / "georgia_supreme_opinions.jsonl", [{"title":"Unsafe URL Case","text":"probable cause","source_url":"http://example.com/case"},{"title":"Script URL Case","text":"probable cause","source_url":"javascript:alert(1)"},{"title":"Safe URL Case","text":"probable cause","source_url":"https://example.com/case"}])
    _empty_supporting_corpora(tmp_path)
    result = legal_search.search_internal("probable cause", "case_analysis")
    by_title = {hit["title"]: hit for hit in result["hits"]}
    assert by_title["Unsafe URL Case"]["source_url"] is None
    assert by_title["Script URL Case"]["source_url"] is None
    assert by_title["Safe URL Case"]["source_url"] == "https://example.com/case"


def test_limit_is_bounded_to_fifty(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    rows=[{"title":f"Case {i}","text":"probable cause","citation":f"{i} Ga. 1"} for i in range(80)]
    _write(tmp_path / "georgia_supreme_opinions.jsonl", rows)
    _empty_supporting_corpora(tmp_path)
    result=legal_search.search_internal("probable cause", "case_analysis", 500)
    assert len(result["hits"]) == 50
