"""AG opinion index discovery must not download PDFs or write corpus rows."""
from backend.app.ingestion.import_ag_opinions import collect_index_pages, discover_report, main


EMPTY = "<table><tr><td>No opinions</td></tr></table>"
LABELED = '<table><tr><td><a href="/opinions/2020-1">2020-1</a></td></tr></table>'


def test_collect_stops_when_page_has_no_citation_labels():
    requested = []

    def fetch(url):
        requested.append(url)
        body = LABELED.encode() if len(requested) == 1 else EMPTY.encode()
        return 200, body

    pages, reason = collect_index_pages(fetch, lambda _seconds: None, 0.5, 40)
    assert reason == "no-citation-labels"
    assert len(pages) == 2
    assert len(requested) == 2
    report = discover_report(pages, fetched_at="2026-10-08T23:00:00+00:00", stopped_reason=reason)
    assert report["committed"] is False
    assert report["corpus_rows_written"] == 0
    assert report["pages"][1]["labels"] == 0
    assert report["pages"][0]["pdf_links"] == 0


def test_discover_refuses_commit_without_database(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert main(["--commit"]) == 1
