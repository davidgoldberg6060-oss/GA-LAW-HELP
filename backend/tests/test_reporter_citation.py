from app.ingestion.reporter_citation import (
    explicit_georgia_reporter_citations,
    resolve_single_georgia_reporter_citation,
)


def test_extracts_explicit_georgia_reports_citation():
    assert explicit_georgia_reporter_citations("Final Copy 321 Ga. 123") == ("321 Ga. 123",)


def test_does_not_turn_docket_number_into_citation():
    assert resolve_single_georgia_reporter_citation("S26A0123 Smith v. State") is None


def test_does_not_promote_southeastern_reporter_alone():
    assert resolve_single_georgia_reporter_citation("900 S.E.2d 42") is None


def test_ambiguous_multiple_georgia_citations_are_not_auto_resolved():
    text="The opinion discusses 320 Ga. 10 and 321 Ga. 123."
    assert explicit_georgia_reporter_citations(text) == ("320 Ga. 10", "321 Ga. 123")
    assert resolve_single_georgia_reporter_citation(text) is None


def test_duplicate_same_citation_is_unambiguous():
    assert resolve_single_georgia_reporter_citation("321 Ga. 123; later 321 Ga. 123") == "321 Ga. 123"


def test_rejects_zero_volume_or_page_and_embedded_numbers():
    assert explicit_georgia_reporter_citations("0 Ga. 1; 321 Ga. 0; x321 Ga. 1234y") == ()
