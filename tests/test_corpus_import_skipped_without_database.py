"""Issue 88: do not invent a corpus when DATABASE_URL is unavailable."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_coverage_ledger_records_skipped_2025_import():
    ledger = (ROOT / "docs" / "GEORGIA_CASE_COVERAGE.md").read_text()
    assert "2026-10-03 17:00 UTC" in ledger
    assert "DATABASE_URL was still unset" in ledger
    assert "import_supreme_opinions --year 2025 --limit 25 --commit" in ledger
    assert "no corpus rows were invented" in ledger
    assert "Issue 88 is not treated as ingested" in ledger
    assert "stored counts were not rechecked" in ledger
