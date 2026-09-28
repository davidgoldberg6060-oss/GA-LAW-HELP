from datetime import datetime, timezone
import json

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


def test_rejects_pdf_until_text_extraction_is_reviewed(monkeypatch):
    monkeypatch.setattr(
        import_one, "production_transport",
        lambda _: fake_response(body=b"%PDF-1.7", content_type="application/pdf"),
    )
    with pytest.raises(ValueError, match="Textual authority required"):
        import_one.prepare("ga_code", URL, "Statute", CITATION)
