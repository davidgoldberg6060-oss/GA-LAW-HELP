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


def test_repeated_same_opinion_link_is_deduplicated():
    html = b'''<a href="/files/s26a0604.pdf">S26A0604. WARE v. THE STATE</a>
    <a href="/files/s26a0604.pdf">S26A0604. WARE v. THE STATE</a>'''

    def transport(url):
        return FetchResponse(url, 200, {"Content-Type": "text/html"}, html)

    opinions = discover(2026, transport)
    assert len(opinions) == 1
    assert opinions[0].docket == "S26A0604"


def test_fails_closed_when_same_docket_points_to_multiple_pdfs():
    html = b'''<a href="/files/s26a0604.pdf">S26A0604. WARE v. THE STATE</a>
    <a href="/files/revised-s26a0604.pdf">S26A0604. WARE v. THE STATE (revised)</a>'''

    def transport(url):
        return FetchResponse(url, 200, {"Content-Type": "text/html"}, html)

    try:
        discover(2026, transport)
    except ValueError as exc:
        assert "Ambiguous court index" in str(exc)
        assert "S26A0604" in str(exc)
    else:
        raise AssertionError("Conflicting PDF provenance for one docket must require review")


def test_fails_closed_when_index_has_no_opinion_documents():
    def transport(url):
        return FetchResponse(url, 200, {"Content-Type": "text/html"}, b"<p>Unavailable</p>")

    try:
        discover(2026, transport)
    except ValueError as exc:
        assert "No opinion PDFs" in str(exc)
    else:
        raise AssertionError("An empty index must not look like a complete import")


def test_commit_refuses_without_explicit_database(monkeypatch, capsys):
    from app.ingestion.import_supreme_opinions import main

    monkeypatch.delenv("DATABASE_URL", raising=False)
    code = main(["--year", "2025", "--limit", "25", "--commit"])
    captured = capsys.readouterr()
    assert code == 2
    assert "DATABASE_URL" in captured.out
    assert '"committed": false' in captured.out
    assert '"attempted": 0' in captured.out


def test_commit_refuses_sqlite_fallback(monkeypatch, capsys):
    from app.ingestion.import_supreme_opinions import main

    monkeypatch.setenv("DATABASE_URL", "sqlite:///./ga_law_help.db")
    code = main(["--year", "2025", "--limit", "25", "--commit"])
    captured = capsys.readouterr()
    assert code == 2
    assert "sqlite" in captured.out
    assert '"succeeded": 0' in captured.out
