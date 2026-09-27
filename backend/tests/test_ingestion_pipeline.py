from types import SimpleNamespace

import pytest

from app.ingestion import pipeline


class FakeDB:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def approved_source():
    return next(iter(pipeline._source_registry().values()))


def item(**overrides):
    source = approved_source()
    values = dict(
        source_name=source.key,
        document=SimpleNamespace(),
        jurisdiction=source.jurisdiction,
        authority_type=source.authority_type,
        citation="123 Ga. 456",
    )
    values.update(overrides)
    return pipeline.IngestionItem(**values)


def test_persist_item_rejects_blank_citation_before_write(monkeypatch):
    called = False

    def fake_upsert(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(pipeline, "upsert_authority_document", fake_upsert)
    with pytest.raises(ValueError, match="verified citation"):
        pipeline.persist_item(FakeDB(), item(citation="   "))
    assert called is False


def test_persist_item_rejects_unapproved_source_before_write(monkeypatch):
    called = False

    def fake_upsert(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(pipeline, "upsert_authority_document", fake_upsert)
    with pytest.raises(ValueError, match="Unsupported Georgia ingestion source"):
        pipeline.persist_item(FakeDB(), item(source_name="random-web-scraper"))
    assert called is False


def test_persist_item_rejects_source_metadata_mismatch(monkeypatch):
    called = False

    def fake_upsert(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(pipeline, "upsert_authority_document", fake_upsert)
    with pytest.raises(ValueError, match="jurisdiction"):
        pipeline.persist_item(FakeDB(), item(jurisdiction="Florida"))
    with pytest.raises(ValueError, match="Authority type"):
        pipeline.persist_item(FakeDB(), item(authority_type="invented_type"))
    assert called is False


def test_persist_item_uses_registry_metadata(monkeypatch):
    captured = {}

    def fake_upsert(db, **kwargs):
        captured.update(kwargs)
        return "saved"

    monkeypatch.setattr(pipeline, "upsert_authority_document", fake_upsert)
    source = approved_source()
    assert pipeline.persist_item(FakeDB(), item()) == "saved"
    assert captured["jurisdiction"] == source.jurisdiction
    assert captured["authority_type"] == source.authority_type


def test_persist_batch_commits_valid_records(monkeypatch):
    db = FakeDB()
    saved = []

    def fake_persist(db_arg, ingestion_item):
        assert db_arg is db
        saved.append(ingestion_item.citation)
        return ingestion_item.citation

    monkeypatch.setattr(pipeline, "persist_item", fake_persist)
    result = pipeline.persist_batch(db, [item(citation="A"), item(citation="B")])
    assert result == ["A", "B"]
    assert saved == ["A", "B"]
    assert db.committed is True
    assert db.rolled_back is False


def test_persist_batch_rolls_back_everything_on_invalid_record(monkeypatch):
    db = FakeDB()

    def fake_persist(db_arg, ingestion_item):
        if ingestion_item.citation == "BAD":
            raise ValueError("invalid authority")
        return ingestion_item.citation

    monkeypatch.setattr(pipeline, "persist_item", fake_persist)
    with pytest.raises(ValueError, match="invalid authority"):
        pipeline.persist_batch(db, [item(citation="GOOD"), item(citation="BAD")])
    assert db.committed is False
    assert db.rolled_back is True


def test_source_for_only_returns_registered_source():
    source = approved_source()
    assert pipeline.source_for(source.key) == source
    with pytest.raises(ValueError, match="Unsupported Georgia ingestion source"):
        pipeline.source_for("not-approved")
