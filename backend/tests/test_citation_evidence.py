from datetime import datetime, timezone

from app.ingestion.citation_evidence import resolve_official_georgia_citation
from app.ingestion.models import LegalStatus, SourceDocument


def _doc(body: bytes, *, content_type="text/html", verification="official"):
    return SourceDocument(
        source_key="georgia_supreme_court",
        url="https://www.gasupreme.us/example",
        title="Final Copy",
        body=body,
        retrieved_at=datetime(2026,9,29,tzinfo=timezone.utc),
        content_type=content_type,
        legal_status=LegalStatus(verification_status=verification),
    )


def test_accepts_single_explicit_reporter_citation_from_official_text():
    assert resolve_official_georgia_citation(_doc(b"Final Copy 321 Ga. 123")) == "321 Ga. 123"


def test_rejects_ambiguous_official_text():
    assert resolve_official_georgia_citation(_doc(b"320 Ga. 10 discusses 321 Ga. 123")) is None


def test_rejects_docket_number_only():
    assert resolve_official_georgia_citation(_doc(b"S26A0123 Smith v. State")) is None


def test_rejects_unverified_text_even_with_reporter_pattern():
    assert resolve_official_georgia_citation(_doc(b"321 Ga. 123",verification="unverified")) is None


def test_pdf_bytes_are_not_naively_decoded_for_citation_evidence():
    assert resolve_official_georgia_citation(_doc(b"%PDF 321 Ga. 123",content_type="application/pdf")) is None
