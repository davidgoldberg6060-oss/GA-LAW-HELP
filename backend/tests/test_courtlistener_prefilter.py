import bz2
import csv
import io

from app.ingestion.courtlistener_prefilter import prefilter
from app.ingestion.import_courtlistener_opinions import csv_rows, opinion_text


def _bulk_csv(rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, doublequote=False, escapechar="\\", lineterminator="\n")
    writer.writerow(["id", "cluster_id", "type", "plain_text", "html_with_citations", "author_str"])
    writer.writerows(rows)
    return buffer.getvalue()


def test_prefilter_keeps_georgia_majority_text_byte_for_byte(tmp_path):
    tricky = 'He said "hi"\n and \\ back\\slash, comma'
    source = _bulk_csv([
        ["1", "42", "020lead", "plain", tricky, "x"],
        ["2", "99", "020lead", "other court", "", ""],
        ["3", "42", "040dissent", "dissent", "", ""],
    ])
    sink = io.StringIO()
    scanned, kept = prefilter(io.StringIO(source), sink, ["42"])
    assert (scanned, kept) == (3, 1)
    path = tmp_path / "opinions-ga-2026-09-30.csv.bz2"
    path.write_bytes(bz2.compress(sink.getvalue().encode("utf-8")))
    rows = list(csv_rows(str(path)))
    original = next(csv.DictReader(io.StringIO(source), escapechar="\\"))
    assert len(rows) == 1 and rows[0]["cluster_id"] == "42" and rows[0]["type"] == "020lead"
    assert rows[0]["html_with_citations"] == tricky
    assert opinion_text(rows[0]) == opinion_text(original)
