from app.ingestion.acquisition import FetchResponse
from app.ingestion.import_supreme_opinions import discover, discover_forthcoming


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


def test_discover_only_counts_index_without_downloading_or_opening_database(monkeypatch, capsys):
    html = b'<a href="/wp-content/uploads/2025/01/s25a0001.pdf">S25A0001. SAMPLE v. THE STATE</a>'

    def transport(url):
        assert url in ("https://www.gasupreme.us/2025-opinions/", "https://www.gasupreme.us/robots.txt")
        if url.endswith("/robots.txt"):
            return FetchResponse(url, 200, {"Content-Type": "text/plain"}, b"User-agent: *\nDisallow: /wp-content/uploads/\n")
        return FetchResponse(url, 200, {"Content-Type": "text/html"}, html)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("discover-only must not acquire PDFs or open a database")

    monkeypatch.setattr("app.ingestion.import_supreme_opinions.production_transport", transport)
    monkeypatch.setattr("app.ingestion.import_supreme_opinions.prepare_opinion", forbidden)
    monkeypatch.setattr("app.ingestion.import_supreme_opinions.SessionLocal", forbidden)
    from app.ingestion.import_supreme_opinions import main

    assert main(["--year", "2025", "--discover-only"]) == 0
    import json
    summary = json.loads(capsys.readouterr().out)
    assert summary["discovered"] == 1
    assert summary["pdfs_downloaded"] == 0
    assert summary["committed"] is False
    assert summary["mode"] == "discover-only"


def test_forthcoming_index_names_uploads_pdfs_without_fetching_them(monkeypatch, capsys):
    html = b'''<a href="/wp-content/uploads/2026/09/s25g1446.pdf">S25G1446, S25G1447. CRAVENS v. SLAUGHTER et al. (two cases)</a>
    <a href="/wp-content/uploads/2026/09/s26a0604.pdf">S26A0604. WARE v. THE STATE</a>
    <a href="/events/oral-argument/">S25G1349. CALENDAR ONLY</a>'''

    def transport(url):
        assert url == "https://www.gasupreme.us/forthcoming-opinions/"
        return FetchResponse("https://www.gasupreme.us/forthcoming-opinions/", 200, {"Content-Type": "text/html"}, html)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("forthcoming inventory must not acquire PDFs or open a database")

    monkeypatch.setattr("app.ingestion.import_supreme_opinions.production_transport", transport)
    monkeypatch.setattr("app.ingestion.import_supreme_opinions.prepare_opinion", forbidden)
    monkeypatch.setattr("app.ingestion.import_supreme_opinions.SessionLocal", forbidden)
    opinions = discover_forthcoming(transport)
    assert [(o.docket, o.url) for o in opinions] == [
        ("S25G1446", "https://www.gasupreme.us/wp-content/uploads/2026/09/s25g1446.pdf"),
        ("S26A0604", "https://www.gasupreme.us/wp-content/uploads/2026/09/s26a0604.pdf"),
    ]
    assert all("/wp-content/uploads/" in o.url for o in opinions)
    from app.ingestion.import_supreme_opinions import main
    import json
    assert main(["--year", "2026", "--discover-only", "--forthcoming"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["discovered"] == 2
    assert summary["attempted"] == 0
    assert summary["committed"] is False
    assert summary["forthcoming"] is True
    assert summary["uploads_blocked"] is True
