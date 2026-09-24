import pytest

from app.ingestion.adapters import (
    CourtOfAppealsOpinionIndexAdapter,
    GeneralAssemblyAdapter,
    GeorgiaCourtsAdapter,
    SupremeCourtOpinionIndexAdapter,
)


def test_supreme_opinion_discovery_deduplicates_case_numbers():
    adapter = SupremeCourtOpinionIndexAdapter()
    items = adapter.discover_from_html("S26A1234 text S26A1234 S26X9999", 2026)
    assert [item.external_id for item in items] == ["S26A1234", "S26X9999"]
    assert all(item.url.startswith("https://www.gasupreme.us/") for item in items)


def test_appeals_opinion_discovery_deduplicates_case_numbers():
    adapter = CourtOfAppealsOpinionIndexAdapter()
    items = adapter.discover_from_html("A26A1234 A26A1234 A26A9999")
    assert [item.external_id for item in items] == ["A26A1234", "A26A9999"]
    assert all(item.url == "https://www.gaappeals.us/opinions/" for item in items)


def test_official_georgia_source_urls_are_internal_registry_targets():
    courts = GeorgiaCourtsAdapter()
    assembly = GeneralAssemblyAdapter()
    assert courts.court_directory().startswith("https://georgiacourts.gov/")
    assert courts.self_help().startswith("https://georgiacourts.gov/")
    assert assembly.code_index() == "https://www.legis.ga.gov/legislation/georgia-code"


def test_supreme_year_bounds_reject_bad_years():
    with pytest.raises(ValueError):
        SupremeCourtOpinionIndexAdapter().year_url(1800)
