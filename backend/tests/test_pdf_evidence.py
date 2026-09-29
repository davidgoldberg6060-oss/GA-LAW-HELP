from datetime import datetime, timezone
from io import BytesIO

from pypdf import PdfWriter

from app.ingestion.models import LegalStatus, SourceDocument
from app.ingestion.pdf_evidence import extract_official_pdf_text, resolve_official_pdf_georgia_citation


def _document(body: bytes, *, verified: bool = True, content_type: str = "application/pdf", title: str = "Example"):
    return SourceDocument(
        source_key="georgia_supreme_court",
        url="https://www.gasupreme.us/wp-content/uploads/2026/01/example.pdf",
        title=title,
        body=body,
        retrieved_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
        content_type=content_type,
        legal_status=LegalStatus(
            verification_status="official" if verified else "unverified",
            status_checked_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
            status_source_url="https://www.gasupreme.us/wp-content/uploads/2026/01/example.pdf",
        ),
    )


def _blank_pdf() -> bytes:
    output=BytesIO()
    writer=PdfWriter()
    writer.add_blank_page(width=612,height=792)
    writer.write(output)
    return output.getvalue()


def test_rejects_unverified_pdf_before_extraction():
    assert extract_official_pdf_text(_document(_blank_pdf(),verified=False)) is None


def test_rejects_non_pdf_content_type():
    assert extract_official_pdf_text(_document(b"321 Ga. 123",content_type="text/plain")) is None


def test_malformed_pdf_is_evidence_failure_not_exception():
    assert extract_official_pdf_text(_document(b"not a pdf 321 Ga. 123")) is None
    assert resolve_official_pdf_georgia_citation(_document(b"not a pdf 321 Ga. 123")) is None


def test_blank_official_pdf_does_not_create_citation():
    document=_document(_blank_pdf())
    assert extract_official_pdf_text(document) is None
    assert resolve_official_pdf_georgia_citation(document) is None


def test_pdf_filename_or_title_never_becomes_citation():
    document=_document(_blank_pdf(), title="321 Ga. 123")
    assert resolve_official_pdf_georgia_citation(document) is None
