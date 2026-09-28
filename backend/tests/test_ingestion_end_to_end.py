from types import SimpleNamespace

import pytest

from app.ingestion import end_to_end
from app.ingestion.acquisition import FetchResponse


class FakeDB:
    pass


def official_response(url="https://www.legis.ga.gov/legislation/georgia-code", body=b"official Georgia authority"):
    return FetchResponse(url=url, status_code=200, headers={"Content-Type": "text/html"}, body=body)


def test_single_import_requires_citation_before_network(monkeypatch):
    called = False

    def transport(url):
        nonlocal called
        called = True
        return official_response(url)

    with pytest.raises(ValueError, match="citation published"):
        end_to_end.acquire_and_persist(
            FakeDB(), source_key="ga_code", url="https://www.legis.ga.gov/legislation/georgia-code",
            title="Code", citation=" ", transport=transport,
        )
    assert called is False


def test_single_import_rejects_unknown_source_before_network():
    called = False

    def transport(url):
        nonlocal called
        called = True
        return official_response(url)

    with pytest.raises(ValueError, match="Unsupported Georgia ingestion source"):
        end_to_end.acquire_and_persist(
            FakeDB(), source_key="unknown", url="https://www.legis.ga.gov/",
            title="Unknown", citation="123 Ga. 1", transport=transport,
        )
    assert called is False


def test_single_import_acquires_then_persists(monkeypatch):
    captured = []

    def fake_ingest(db, records):
        captured.extend(records)
        return ["saved-authority"]

    monkeypatch.setattr(end_to_end, "ingest_verified_batch", fake_ingest)
    result = end_to_end.acquire_and_persist(
        FakeDB(), source_key="ga_code", url="https://www.legis.ga.gov/legislation/georgia-code",
        title="Georgia Code", citation="O.C.G.A. test citation",
        transport=lambda url: official_response(url),
    )
    assert result == "saved-authority"
    assert captured[0][0] == "ga_code"
    assert captured[0][2] == "O.C.G.A. test citation"
    assert captured[0][1].source_key == "ga_code"


def test_batch_validation_finishes_before_any_persistence(monkeypatch):
    persisted = False

    def fake_ingest(db, records):
        nonlocal persisted
        persisted = True
        return records

    monkeypatch.setattr(end_to_end, "ingest_verified_batch", fake_ingest)
    records = [
        {"source_key": "ga_code", "url": "https://www.legis.ga.gov/legislation/georgia-code", "title": "Code", "citation": "citation one"},
        {"source_key": "ga_code", "url": "https://example.com/not-official", "title": "Bad", "citation": "citation two"},
    ]
    with pytest.raises(ValueError):
        end_to_end.acquire_and_persist_batch(FakeDB(), records, transport=lambda url: official_response(url))
    assert persisted is False


def test_batch_missing_later_citation_never_persists(monkeypatch):
    persisted = False

    def fake_ingest(db, records):
        nonlocal persisted
        persisted = True
        return records

    monkeypatch.setattr(end_to_end, "ingest_verified_batch", fake_ingest)
    records = [
        {"source_key": "ga_code", "url": "https://www.legis.ga.gov/legislation/georgia-code", "title": "Code", "citation": "citation one"},
        {"source_key": "ga_code", "url": "https://www.legis.ga.gov/legislation/georgia-code", "title": "Code 2", "citation": ""},
    ]
    with pytest.raises(ValueError, match="Every authority requires"):
        end_to_end.acquire_and_persist_batch(FakeDB(), records, transport=lambda url: official_response(url))
    assert persisted is False
