from types import SimpleNamespace

import pytest

from app.ingestion.pipeline import IngestionItem
from app.ingestion.models import LegalStatus, SourceDocument
from app.ingestion.supreme_end_to_end import SupremeAcquisitionResult
import app.ingestion.supreme_persistence as subject


def _item(citation="321 Ga. 123"):
    return IngestionItem(
        source_name="georgia_supreme_court",
        document=SourceDocument(
            source_key="georgia_supreme_court",
            url="https://www.gasupreme.us/example.pdf",
            title="Example",
            body=b"pdf",
            retrieved_at=None,
            content_type="application/pdf",
            legal_status=LegalStatus(verification_status="official"),
        ),
        jurisdiction="Georgia",
        authority_type="case_law",
        citation=citation,
    )


def test_empty_acquisition_does_not_open_persistence_batch(monkeypatch):
    monkeypatch.setattr(subject, "acquire_discovered_supreme_opinions", lambda *a, **k: SupremeAcquisitionResult((), ({"reason":"no citation"},)))
    monkeypatch.setattr(subject, "persist_batch", lambda *a, **k: pytest.fail("persist_batch must not run"))
    result=subject.acquire_and_persist_supreme_opinions(object(), "html", page_url="https://www.gasupreme.us/opinions/", transport=lambda u: None)
    assert result.discovered_for_index == 0
    assert result.persisted == 0
    assert result.skipped[0]["reason"] == "no citation"


def test_qualifying_items_are_persisted_as_one_batch(monkeypatch):
    items=(_item(), _item("322 Ga. 1"))
    monkeypatch.setattr(subject, "acquire_discovered_supreme_opinions", lambda *a, **k: SupremeAcquisitionResult(items, ()))
    seen=[]
    monkeypatch.setattr(subject, "persist_batch", lambda db, batch: seen.extend(batch) or [object(), object()])
    result=subject.acquire_and_persist_supreme_opinions(object(), "html", page_url="https://www.gasupreme.us/opinions/", transport=lambda u: None)
    assert seen == list(items)
    assert result.discovered_for_index == 2
    assert result.persisted == 2


def test_persistence_failure_is_not_hidden(monkeypatch):
    monkeypatch.setattr(subject, "acquire_discovered_supreme_opinions", lambda *a, **k: SupremeAcquisitionResult((_item(),), ()))
    def fail(db, batch):
        raise RuntimeError("database write failed")
    monkeypatch.setattr(subject, "persist_batch", fail)
    with pytest.raises(RuntimeError, match="database write failed"):
        subject.acquire_and_persist_supreme_opinions(object(), "html", page_url="https://www.gasupreme.us/opinions/", transport=lambda u: None)
