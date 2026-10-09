"""Court of Appeals discover-only must not download opinion PDFs or open a database."""
import json

from backend.app.ingestion.import_appeals_opinions import discover_index, main


class _Response:
    def __init__(self, url, status, body):
        self.url = url
        self.status_code = status
        self.body = body
        self.headers = {"content-type": "text/html"}


def test_discover_index_hashes_pages_and_skips_pdfs():
    calls = []

    def transport(url):
        calls.append(url)
        return _Response(url, 405, b"<title>Human Verification</title>")

    report = discover_index(transport)
    assert calls == [
        "https://www.gaappeals.gov/opinion-search/",
        "https://www.gaappeals.gov/robots.txt",
    ]
    assert report["committed"] is False
    assert report["pdfs_downloaded"] == 0
    assert report["search_endpoint_requested"] is False
    assert all(page["downloaded_pdfs"] == 0 and page["pdf_links_named"] == 0 for page in report["pages"])
    assert all(page["waf_captcha"] is True for page in report["pages"])
    assert "efast.gaappeals.gov" not in " ".join(calls)


def test_discover_only_refuses_commit(capsys):
    try:
        main(["--discover-only", "--commit"], transport=lambda url: _Response(url, 200, b""))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("discover-only --commit should fail")
    assert "efast" not in capsys.readouterr().out


def test_commit_refuses_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    try:
        main(["--start", "2026-01-01", "--end", "2026-01-02", "--commit"], transport=lambda url: (_ for _ in ()).throw(AssertionError("should not fetch")))
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("commit without DATABASE_URL should fail")
