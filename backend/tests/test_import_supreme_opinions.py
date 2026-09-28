from app.ingestion.acquisition import FetchResponse
from app.ingestion.import_supreme_opinions import discover


def test_discovers_official_opinion_pdf_and_ignores_external_links():
    html = b'''<a href="/wp-content/uploads/2026/09/s26a0604.pdf">S26A0604. WARE v. THE STATE</a>
    <a href="https://example.com/bogus.pdf">S26A9999. BOGUS</a>
    <a href="/2026-opinions/">S26A8888. INDEX</a>'''

    def transport(url):
        assert url == "https://www.gasupreme.us/2026-opinions/"
        return FetchResponse(url, 200, {"Content-Type": "text/html; charset=utf-8"}, html)

    opinions = discover(2026, transport)
    assert [(o.docket, o.url) for o in opinions] == [
        ("S26A0604", "https://www.gasupreme.us/wp-content/uploads/2026/09/s26a0604.pdf")
    ]


def test_fails_closed_when_index_has_no_opinion_documents():
    def transport(url):
        return FetchResponse(url, 200, {"Content-Type": "text/html"}, b"<p>Unavailable</p>")

    try:
        discover(2026, transport)
    except ValueError as exc:
        assert "No opinion PDFs" in str(exc)
    else:
        raise AssertionError("An empty index must not look like a complete import")
