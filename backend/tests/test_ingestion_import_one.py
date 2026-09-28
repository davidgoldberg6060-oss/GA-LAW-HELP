from datetime import datetime, timezone
import json
from io import BytesIO

from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

import pytest

from app.ingestion import import_one
from app.ingestion.acquisition import FetchResponse


URL = "https://www.legis.ga.gov/legislation/12345"
CITATION = "O.C.G.A. § 1-1-1"


def fake_response(url=URL, body=None, content_type="text/html"):
    return FetchResponse(
        url=url,
        status_code=200,
        headers={"Content-Type": content_type},
        body=body or f"<html><body>{CITATION} currently effective</body></html>".encode(),
    )


def test_preview_requires_no_database_write(monkeypatch, capsys):
    monkeypatch.setattr(import_one, "production_transport", lambda _: fake_response())
    def should_not_open_db():
        raise AssertionError("preview opened the database")
    monkeypatch.setattr(import_one, "SessionLocal", should_not_open_db)
    assert import_one.main([
        "--source", "ga_code", "--url", URL,
        "--title", "Individual statute", "--citation", CITATION,
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["mode"] == "preview"
    assert result["authority_id"] is None
    assert result["currency_status"] == "unknown"
    assert result["precedential_status"] == "unknown"
    assert len(result["sha256"]) == 64


def test_citation_must_be_visible_on_official_document(monkeypatch):
    monkeypatch.setattr(
        import_one, "production_transport",
        lambda _: fake_response(body=b"<html><script>O.C.G.A. &sect; 1-1-1</script><body>other</body></html>"),
    )
    with pytest.raises(ValueError, match="Citation is absent"):
        import_one.prepare("ga_code", URL, "Statute", CITATION)


def test_rejects_index_and_cross_source_documents(monkeypatch):
    monkeypatch.setattr(import_one, "production_transport", lambda _: fake_response())
    with pytest.raises(ValueError, match="source index"):
        import_one.prepare("ga_code", "https://www.legis.ga.gov/legislation/georgia-code", "Index", CITATION)
    with pytest.raises(ValueError, match="selected source"):
        import_one.prepare("ga_code", "https://georgiacourts.gov/rules/example", "Rule", CITATION)


def test_rejects_malformed_pdf(monkeypatch):
    monkeypatch.setattr(
        import_one, "production_transport",
        lambda _: fake_response(body=b"%PDF-1.7", content_type="application/pdf"),
    )
    with pytest.raises(ValueError, match="Unable to extract official PDF text"):
        import_one.prepare("ga_code", URL, "Statute", CITATION)


def test_extracts_official_pdf_and_preserves_original_hash(monkeypatch):
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})
    })
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 72 720 Td (Uniform Superior Court Rules Rule 1 Preamble official Georgia rule text.) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    pdf = output.getvalue()
    pdf_url = "https://assets.georgiacourts.gov/rules.pdf"
    monkeypatch.setattr(
        import_one, "production_transport",
        lambda _: fake_response(url=pdf_url, body=pdf, content_type="application/pdf"),
    )
    item = import_one.prepare(
        "ga_court_rules", pdf_url, "Uniform Superior Court Rules",
        "Uniform Superior Court Rules",
    )
    assert item.document.body == pdf
    assert item.document.extracted_text.startswith("Uniform Superior Court Rules")
    assert item.document.legal_status.currency_status == "unknown"
