from datetime import datetime, timezone

import pytest

from app.ingestion.acquisition import FetchResponse
from app.ingestion.source_acquisition import OfficialDocumentRequest, acquire_ingestion_item, acquire_many


def _transport(url: str):
    return FetchResponse(
        url=url,
        status_code=200,
        headers={"content-type": "text/html; charset=utf-8"},
        body=b"<html><body>Official Georgia legal document</body></html>",
    )


def test_acquisition_requires_source_published_citation():
    request=OfficialDocumentRequest(
        source_key="georgia_supreme_court",
        url="https://www.gasupreme.us/wp-content/uploads/2026/01/example.pdf",
        title="Example opinion",
    )
    with pytest.raises(ValueError, match="no source-published citation"):
        acquire_ingestion_item(request,transport=_transport)


def test_acquisition_preserves_supplied_citation_and_source_metadata():
    request=OfficialDocumentRequest(
        source_key="georgia_supreme_court",
        url="https://www.gasupreme.us/wp-content/uploads/2026/01/example.pdf",
        title="Example opinion",
        citation="321 Ga. 123",
        external_id="S26A0001",
    )
    item=acquire_ingestion_item(request,transport=_transport,retrieved_at=datetime(2026,9,28,tzinfo=timezone.utc))
    assert item.citation=="321 Ga. 123"
    assert item.document.external_id=="S26A0001"
    assert item.jurisdiction=="Georgia"
    assert item.document.url.startswith("https://")


def test_deterministic_resolver_can_supply_citation_from_official_document():
    request=OfficialDocumentRequest(
        source_key="georgia_supreme_court",
        url="https://www.gasupreme.us/wp-content/uploads/2026/01/example.pdf",
        title="Example opinion",
    )
    item=acquire_ingestion_item(request,transport=_transport,citation_resolver=lambda document:"321 Ga. 456")
    assert item.citation=="321 Ga. 456"


def test_batch_isolates_unverifiable_document_without_inventing_citation():
    requests=[
        OfficialDocumentRequest("georgia_supreme_court","https://www.gasupreme.us/wp-content/uploads/2026/01/a.pdf","A","321 Ga. 1"),
        OfficialDocumentRequest("georgia_supreme_court","https://www.gasupreme.us/wp-content/uploads/2026/01/b.pdf","B"),
    ]
    items,skipped=acquire_many(requests,transport=_transport)
    assert [item.citation for item in items]==["321 Ga. 1"]
    assert len(skipped)==1
    assert "no source-published citation" in skipped[0]["reason"]
