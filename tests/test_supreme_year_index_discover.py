from backend.app.ingestion.import_supreme_opinions import discover_year_index, main


class _Response:
    def __init__(self, url, status, body):
        self.url = url
        self.status_code = status
        self.body = body
        self.headers = [("content-type", "text/html")]


HTML = """
<html><body>
<a href="https://www.gasupreme.us/wp-content/uploads/2024/12/s24a0894.pdf">S24A0894. WILLIAMS v. THE STATE</a>
</body></html>
"""


def test_year_index_hashes_page_and_does_not_fetch_pdfs():
    seen = []

    def transport(url):
        seen.append(url)
        if url.endswith("robots.txt"):
            return _Response(url, 200, b"User-agent: *\nDisallow: /wp-content/uploads/\n")
        return _Response(url, 200, HTML.encode())

    report = discover_year_index(2024, transport)
    assert report["mode"] == "discover-only"
    assert report["committed"] is False
    assert report["pdfs_downloaded"] == 0
    assert report["discovered"] == 1
    assert report["uploads_blocked"] is True
    assert report["opinions"][0]["docket"] == "S24A0894"
    assert report["opinions"][0]["gap"].startswith("Index label only")
    assert all(not item.endswith(".pdf") for item in seen)
    assert report["pages"][0]["sha256"]
    assert report["pages"][0]["downloaded_pdfs"] == 0


def test_discover_only_refuses_commit():
    try:
        main(["--year", "2024", "--discover-only", "--commit"])
    except SystemExit:
        return
    raise AssertionError("discover-only --commit should fail")


def test_commit_refuses_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    try:
        main(["--year", "2024", "--commit"])
    except SystemExit:
        return
    raise AssertionError("commit without DATABASE_URL should fail")
