from scripts.record_corpus_import_attempt import attempt_record


def test_missing_database_url_does_not_invent_corpus():
    record = attempt_record(None)
    assert record["status"] == "skipped"
    assert record["committed"] is False
    assert record["rows_written"] is None
    assert record["database_url_available"] is False
    assert "invented" in record["reason"]


def test_present_database_url_still_does_not_imply_ingestion():
    record = attempt_record("postgresql+psycopg://example")
    assert record["database_url_available"] is True
    assert record["committed"] is False
    assert record["rows_written"] is None
