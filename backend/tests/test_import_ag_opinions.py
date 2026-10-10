import json

from app.ingestion.import_ag_opinions import discover_report, main, parse_index

FIXTURE = """
<table>
<tr><td><a href="/opinions/u2026-1">U2026-1</a></td>
<td>Read a PDF copy <a href="https://law.georgia.gov/document/document/81726-unofficial-ag-opinionpdf/download">opinion</a></td></tr>
<tr><td><a href="/opinions/2026-2">2026-2</a></td>
<td><a href="https://law.georgia.gov/document/document/032426-official-ag-opinionpdf--UNPUBLISHED-document--DO-NOT-SHARE-this-URL--/download">here</a></td></tr>
<tr><td><a href="/opinions">Official Opinions</a></td></tr>
</table>
"""


def test_parse_index_keeps_labels_and_does_not_treat_nav_as_opinions():
    rows = parse_index(FIXTURE, page_url="https://law.georgia.gov/opinions")
    assert [row["citation"] for row in rows] == ["U2026-1", "2026-2"]
    assert rows[1]["gap"].startswith("Index names an unpublished PDF URL")
    assert "DO-NOT-SHARE" in rows[1]["pdf_url"]


def test_discover_report_counts_labels_without_claiming_stored_text():
    report = discover_report(
        [{"url": "https://law.georgia.gov/opinions", "bytes": 10, "sha256": "abc", "html": FIXTURE}],
        fetched_at="2026-10-08T22:00:00+00:00",
    )
    assert report["committed"] is False
    assert report["corpus_rows_written"] == 0
    assert report["opinion_labels"] == 2
    assert report["pdf_links_named"] == 2
    assert report["unpublished_pdf_urls_not_fetched"]


def test_commit_refused_when_database_url_unset(monkeypatch, capsys):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert main(["--commit"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["committed"] is False
    assert "DATABASE_URL" in payload["reason"]
