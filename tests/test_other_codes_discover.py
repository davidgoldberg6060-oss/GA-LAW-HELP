"""Other-codes index inventory must not download PDFs or open a database."""
from backend.app.ingestion.import_court_rules import discover_other_codes, main


INDEX = """
<a href="/wp-content/uploads/2024/02/Code-of-Judicial-Conduct-2024_02_01.pdf">Code</a>
<a href="https://www.gasupreme.us/wp-content/uploads/2018/06/UNIFIED_APPEAL-06_06_18.pdf">UAP</a>
<a href="https://example.com/not-official.pdf">offsite</a>
"""


def test_discover_other_codes_lists_official_pdfs_only():
    report = discover_other_codes(
        INDEX,
        source_url="https://www.gasupreme.us/other-codes-rules/",
        fetched_at="2026-10-08T20:01:00+00:00",
        sha256="abc",
        index_bytes=12,
        robots_disallow_uploads=True,
    )
    assert report["committed"] is False
    assert report["mode"] == "discover-only"
    assert report["pdf_links"] == 2
    assert report["pdfs"][0]["downloaded"] is False
    assert report["pdfs"][0]["url"].endswith("Code-of-Judicial-Conduct-2024_02_01.pdf")
    assert "not downloaded" in report["pdfs"][0]["gap"]
    assert report["robots_disallow_uploads"] is True
    assert all("example.com" not in item["url"] for item in report["pdfs"])


def test_discover_other_codes_refuses_commit():
    try:
        main(["--discover-other-codes", "--commit"], fetch=lambda url, limit: None, sleep=lambda _seconds: None)
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("discover-other-codes --commit should fail")
