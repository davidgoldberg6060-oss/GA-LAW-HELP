from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_legal_forms_use_distinct_official_indexes():
    catalog = (ROOT / "src" / "approvedScreenCatalog.ts").read_text()
    criminal = "https://georgiacourts.gov/inmate-forms/"
    civil = "https://georgiacourts.gov/forms-and-records/"
    family = "https://georgiacourts.gov/a2j/self-help-resources/family-law/"
    assert criminal in catalog
    assert civil in catalog
    assert family in catalog
    assert len({criminal, civil, family}) == 3
    assert "lexis" not in catalog.lower()
    assert "Do not resist" in catalog
