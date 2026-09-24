from app.motion_discovery import discover_procedures, discover_from_authorities


def test_discovers_common_procedure_phrases_without_calling_them_verified():
    text = "The defendant filed a motion to suppress evidence. Later, a motion for new trial was filed."
    rows = discover_procedures(text, authority_id=7, citation="Example", authority_status="UNVERIFIED")
    names = {row["normalized_name"] for row in rows}
    assert "motion to suppress evidence" in names
    assert "motion for new trial" in names
    assert all(row["authority_status"] == "UNVERIFIED" for row in rows)


def test_counts_repeated_mentions():
    rows = discover_procedures("A motion to dismiss was filed. The motion to dismiss was denied.")
    row = next(item for item in rows if item["normalized_name"] == "motion to dismiss")
    assert row["occurrence_count"] == 2


def test_aggregates_authority_references():
    class Authority:
        def __init__(self, ident, citation, text):
            self.id = ident
            self.citation = citation
            self.text = text
            self.source_url = "https://example.test/official"
            self.status = "CURRENT"

    rows = discover_from_authorities([
        Authority(1, "A", "A motion for new trial was filed."),
        Authority(2, "B", "The motion for new trial was denied."),
    ])
    row = next(item for item in rows if item["normalized_name"] == "motion for new trial")
    assert row["occurrence_count"] == 2
    assert len(row["authority_refs"]) == 2
