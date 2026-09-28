from datetime import datetime, timezone

import pytest

from app.ingestion import acquisition


def response(url, *, status=200, content_type="text/html", body=b"official text"):
    return acquisition.FetchResponse(
        url=url,
        status_code=status,
        headers={"Content-Type": content_type},
        body=body,
    )


def acquire(fetch_response):
    return acquisition.acquire_official_document(
        source_key="ga_code",
        url="https://www.legis.ga.gov/legislation/georgia-code",
        title="Georgia Code",
        transport=lambda _: fetch_response,
        retrieved_at=datetime(2026, 9, 27, tzinfo=timezone.utc),
    )


def test_accepts_registered_official_html_and_preserves_provenance():
    doc = acquire(response("https://www.legis.ga.gov/legislation/georgia-code"))
    assert doc.source_key == "ga_code"
    assert doc.content_type == "text/html"
    assert doc.metadata["jurisdiction"] == "Georgia"
    assert doc.metadata["authority_type"] == "statute"
    assert doc.legal_status.verification_status == "official"


def test_revalidates_redirect_destination():
    with pytest.raises(ValueError):
        acquire(response("https://example.com/copied-law"))


def test_rejects_non_success_response():
    with pytest.raises(ValueError, match="HTTP 404"):
        acquire(response("https://www.legis.ga.gov/missing", status=404))


def test_rejects_empty_document():
    with pytest.raises(ValueError, match="empty document"):
        acquire(response("https://www.legis.ga.gov/legislation/georgia-code", body=b""))


def test_rejects_oversized_document(monkeypatch):
    monkeypatch.setattr(acquisition, "MAX_DOCUMENT_BYTES", 3)
    with pytest.raises(ValueError, match="size limit"):
        acquire(response("https://www.legis.ga.gov/legislation/georgia-code", body=b"1234"))


def test_rejects_missing_or_unsupported_content_type():
    with pytest.raises(ValueError, match="content type"):
        acquire(response("https://www.legis.ga.gov/legislation/georgia-code", content_type="application/octet-stream"))


def test_pdf_does_not_infer_current_or_precedential_status():
    doc = acquire(response(
        "https://www.legis.ga.gov/document.pdf",
        content_type="application/pdf",
        body=b"%PDF fake test payload",
    ))
    assert doc.legal_status.verification_status == "official"
    assert doc.legal_status.currency_status == "unknown"
    assert doc.legal_status.precedential_status == "unknown"


def test_text_status_only_uses_explicit_official_evidence():
    unknown = acquire(response(
        "https://www.legis.ga.gov/legislation/georgia-code",
        body=b"Georgia legal material without a currency statement",
    ))
    assert unknown.legal_status.currency_status == "unknown"

    current = acquire(response(
        "https://www.legis.ga.gov/legislation/georgia-code",
        body=b"This provision is currently effective.",
    ))
    assert current.legal_status.currency_status == "current"
