import json

from app import internal_legal_search as legal_search


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


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


def test_case_lookup_routes_only_cases_and_statutes(tmp_path, monkeypatch):
    _fixture_corpus(tmp_path, monkeypatch)
    result = legal_search.search_internal("burglary", "case_lookup")
    assert result["hits"]
    assert {hit["corpus"] for hit in result["hits"]} <= {"cases", "statutes"}
    assert any(hit["citation"] == "O.C.G.A. § 16-7-1" for hit in result["hits"])


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


def test_limit_is_bounded_to_fifty(tmp_path, monkeypatch):
    monkeypatch.setattr(legal_search, "CORPUS", tmp_path)
    rows=[{"title":f"Case {i}","text":"probable cause","citation":f"{i} Ga. 1"} for i in range(80)]
    _write(tmp_path / "georgia_supreme_opinions.jsonl", rows)
    _write(tmp_path / "georgia_court_of_appeals.jsonl", [])
    _write(tmp_path / "georgia_statutes.jsonl", [])
    _write(tmp_path / "georgia_rules_motions.jsonl", [])
    _write(tmp_path / "law_enforcement_authorities.jsonl", [])
    result=legal_search.search_internal("probable cause", "case_analysis", 500)
    assert len(result["hits"]) == 50
