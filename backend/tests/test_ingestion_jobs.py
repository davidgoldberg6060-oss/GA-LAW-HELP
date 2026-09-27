from types import SimpleNamespace

import pytest

from app.ingestion import jobs


@pytest.mark.parametrize(
    "function_name,source_key",
    [
        ("ingest_georgia_code", "ga_code"),
        ("ingest_georgia_legislation", "ga_legislation"),
        ("ingest_georgia_court_rule", "ga_court_rules"),
        ("ingest_supreme_court_rule", "ga_supreme_rules"),
        ("ingest_supreme_court_opinion", "ga_supreme_opinions"),
        ("ingest_court_of_appeals_opinion", "ga_appeals_opinions"),
    ],
)
def test_job_uses_canonical_source_metadata(monkeypatch, function_name, source_key):
    document = SimpleNamespace()
    canonical = SimpleNamespace(key=source_key, jurisdiction="Georgia", authority_type="case_law")
    captured = {}

    monkeypatch.setattr(jobs, "source_for", lambda key: canonical if key == source_key else None)

    def fake_persist(db, item):
        captured["item"] = item
        return "saved"

    monkeypatch.setattr(jobs, "persist_item", fake_persist)
    result = getattr(jobs, function_name)(object(), document, "OFFICIAL-CITATION")

    assert result == "saved"
    item = captured["item"]
    assert item.source_name == source_key
    assert item.document is document
    assert item.jurisdiction == canonical.jurisdiction
    assert item.authority_type == canonical.authority_type
    assert item.citation == "OFFICIAL-CITATION"


def test_blank_citation_reaches_pipeline_guard(monkeypatch):
    canonical = SimpleNamespace(key="ga_code", jurisdiction="Georgia", authority_type="statute")
    monkeypatch.setattr(jobs, "source_for", lambda key: canonical)

    def guarded_persist(db, item):
        if not item.citation.strip():
            raise ValueError("verified citation required")

    monkeypatch.setattr(jobs, "persist_item", guarded_persist)
    with pytest.raises(ValueError, match="verified citation"):
        jobs.ingest_georgia_code(object(), SimpleNamespace(), "   ")


def test_verified_batch_uses_source_registry_for_every_record(monkeypatch):
    sources = {
        "ga_code": SimpleNamespace(key="ga_code", jurisdiction="Georgia", authority_type="statute"),
        "ga_supreme_opinions": SimpleNamespace(key="ga_supreme_opinions", jurisdiction="Georgia", authority_type="case_law"),
    }
    monkeypatch.setattr(jobs, "source_for", lambda key: sources[key])
    captured = {}

    def fake_batch(db, items):
        captured["items"] = items
        return items

    monkeypatch.setattr(jobs, "persist_batch", fake_batch)
    result = jobs.ingest_verified_batch(
        object(),
        [
            ("ga_code", SimpleNamespace(), "O.C.G.A. TEST"),
            ("ga_supreme_opinions", SimpleNamespace(), "CASE TEST"),
        ],
    )
    assert result == captured["items"]
    assert [item.authority_type for item in result] == ["statute", "case_law"]
    assert [item.citation for item in result] == ["O.C.G.A. TEST", "CASE TEST"]
