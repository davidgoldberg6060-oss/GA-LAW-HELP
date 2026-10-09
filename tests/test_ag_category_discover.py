"""AG category index inventory must not download PDFs or open a database."""
from backend.app.ingestion.import_ag_opinions import discover_categories, main

INDEX = """
<tr><td><a href="/opinions/2026-2">2026-2</a>
<a href="/document/document/032426-official-ag-opinionpdf--UNPUBLISHED-document--DO-NOT-SHARE-this-URL--/download">PDF</a></td></tr>
<tr><td><a href="/opinions/U2024-1">U2024-1</a></td></tr>
"""


def test_discover_categories_lists_labels_without_pdf_bytes():
    report = discover_categories(
        [{
            "category": "official",
            "url": "https://law.georgia.gov/opinions/official",
            "bytes": 10,
            "sha256": "abc",
            "html": INDEX,
        }],
        fetched_at="2026-10-09T00:01:00+00:00",
    )
    assert report["committed"] is False
    assert report["corpus_rows_written"] == 0
    assert report["mode"] == "discover-only"
    assert report["categories"] == ["official"]
    assert report["opinion_labels"] == 2
    assert report["unpublished_pdf_urls_not_fetched"]
    assert "not downloaded" in report["gap"].lower() or "not downloaded" in report["gap"]


def test_discover_categories_refuses_commit():
    try:
        main(["--discover-categories", "--commit"])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("discover-categories --commit should fail")
