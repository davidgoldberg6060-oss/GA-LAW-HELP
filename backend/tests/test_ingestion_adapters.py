import pytest

from app.ingestion.adapters import (
    CourtOfAppealsOpinionIndexAdapter,
    GeneralAssemblyAdapter,
    GeorgiaCourtsAdapter,
    SupremeCourtOpinionIndexAdapter,
    official_georgia_authority_sources,
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


def test_authority_registry_covers_core_georgia_primary_sources():
    sources = official_georgia_authority_sources()
    keys = {source.key for source in sources}
    assert {"ga_code", "ga_legislation", "ga_court_rules", "ga_supreme_rules", "ga_supreme_opinions", "ga_appeals_opinions"} <= keys
    assert all(source.official for source in sources)
    assert all(source.jurisdiction == "Georgia" for source in sources)
    assert all(source.url.startswith("https://") for source in sources)
    assert {source.authority_type for source in sources} >= {"statute", "legislation", "court_rule", "case_law"}


def test_registry_does_not_claim_legal_status_for_entry_points():
    # Registry membership is provenance, not a citator result.
    for source in official_georgia_authority_sources():
        assert not hasattr(source, "currency_status")
        assert not hasattr(source, "precedential_status")


def test_supreme_year_bounds_reject_bad_years():
    with pytest.raises(ValueError):
        SupremeCourtOpinionIndexAdapter().year_url(1800)
