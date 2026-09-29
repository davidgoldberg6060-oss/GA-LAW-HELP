import pytest

from app.ingestion.acquisition import FetchResponse
from app.ingestion.import_supreme_opinions import Opinion, prepare_opinion


def test_docket_is_never_used_as_reporter_citation():
    opinion = Opinion(
        docket="S26A0123",
        title="S26A0123 Example v. State",
        url="https://www.gasupreme.us/wp-content/uploads/2026/01/example.pdf",
    )

    def transport(url: str):
        return FetchResponse(
            url=url,
            status_code=200,
            headers={"content-type": "application/pdf"},
            body=b"%PDF-1.4\nS26A0123 Example v. State\n%%EOF",
        )

    with pytest.raises(ValueError):
        prepare_opinion(opinion, transport=transport)


def test_external_id_remains_docket_when_citation_evidence_is_resolved(monkeypatch):
    opinion = Opinion(
        docket="S26A0123",
        title="S26A0123 Example v. State",
        url="https://www.gasupreme.us/wp-content/uploads/2026/01/example.pdf",
    )

    def transport(url: str):
        return FetchResponse(
            url=url,
            status_code=200,
            headers={"content-type": "application/pdf"},
            body=b"%PDF-1.4\nplaceholder\n%%EOF",
        )

    monkeypatch.setattr(
        "app.ingestion.import_supreme_opinions.resolve_official_pdf_georgia_citation",
        lambda document: "321 Ga. 123",
    )
    item = prepare_opinion(opinion, transport=transport)
    assert item.citation == "321 Ga. 123"
    assert item.document.external_id == "S26A0123"
    assert item.citation != item.document.external_id
