from types import SimpleNamespace

from app.ingestion.coverage import corpus_coverage


class Query:
    def __init__(self, rows): self.rows = rows
    def filter(self, *_args, **_kwargs): return self
    def all(self): return self.rows


class DB:
    def __init__(self, rows): self.rows = rows
    def query(self, *_args): return Query(self.rows)


def authority(**changes):
    base = dict(
        authority_type="case",
        status="VERIFIED",
        citation="123 Ga. 456",
        source_url="https://www.gasupreme.us/example",
        currency_status="unknown",
        precedential_status="unknown",
        negative_treatment="",
        status_checked_at=None,
        status_source_url=None,
    )
    base.update(changes)
    return SimpleNamespace(**base)


def test_coverage_counts_only_stored_records_and_disclaims_completeness():
    report = corpus_coverage(DB([
        authority(),
        authority(authority_type="statute", status="UNVERIFIED", citation="O.C.G.A. 1-1-1"),
    ]))
    assert report["total_authorities"] == 2
    assert report["verified_authorities"] == 1
    assert report["traceable_verified_authorities"] == 1
    assert report["completeness_claimed"] is False
    assert "do not prove" in report["coverage_notice"]


def test_coverage_tracks_status_checks_and_negative_treatment():
    report = corpus_coverage(DB([
        authority(status_checked_at="2026-09-28", status_source_url="https://www.gasupreme.us/status"),
        authority(currency_status="overruled"),
    ]))
    assert report["verified_with_status_check"] == 1
    assert report["negative_treatment_records"] == 1


def test_coverage_reports_actionable_stored_record_quality_gaps_without_estimating_missing_law():
    report = corpus_coverage(DB([
        authority(),
        authority(status="UNVERIFIED", citation="", source_url="http://example.test/source"),
        authority(currency_status="current", precedential_status="binding", status_checked_at="2026-09-28", status_source_url="https://www.gasupreme.us/status"),
    ]))
    gaps = report["quality_gaps"]
    assert gaps["records_missing_citation"] == 1
    assert gaps["records_missing_https_source"] == 1
    assert gaps["records_not_verified"] == 1
    assert gaps["verified_missing_status_check"] == 1
    assert gaps["verified_unknown_currency"] == 1
    assert gaps["verified_unknown_precedential_status"] == 1
    assert report["completeness_claimed"] is False
    assert "must not be interpreted as an estimate" in report["coverage_notice"]
