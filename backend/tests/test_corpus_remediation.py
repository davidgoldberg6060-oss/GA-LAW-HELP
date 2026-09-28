from types import SimpleNamespace

import pytest

from app.ingestion.remediation import remediation_records


class Query:
    def __init__(self, rows): self.rows = rows
    def filter(self, *_args, **_kwargs): return self
    def all(self): return self.rows


class DB:
    def __init__(self, rows): self.rows = rows
    def query(self, *_args): return Query(self.rows)


def authority(id, **changes):
    base = dict(
        id=id,
        title=f"Authority {id}",
        citation="123 Ga. 456",
        source_url="https://www.gasupreme.us/example",
        status="VERIFIED",
        currency_status="current",
        precedential_status="binding",
        status_checked_at="2026-09-28",
        status_source_url="https://www.gasupreme.us/status",
    )
    base.update(changes)
    return SimpleNamespace(**base)


def test_remediation_records_selects_only_requested_gap_and_does_not_fill_missing_values():
    rows = [
        authority(2, citation=""),
        authority(1, citation="", source_url=None),
        authority(3),
    ]
    work = remediation_records(DB(rows), "citation_provenance")
    assert [item["authority_id"] for item in work] == [1, 2]
    assert work[0]["citation"] is None
    assert work[0]["requires_authoritative_source"] is True


def test_status_remediation_applies_only_to_verified_records():
    rows = [
        authority(1, status_checked_at=None, status_source_url=None),
        authority(2, status="UNVERIFIED", status_checked_at=None, status_source_url=None),
    ]
    assert [item["authority_id"] for item in remediation_records(DB(rows), "status_check")] == [1]


def test_remediation_is_bounded_and_rejects_unknown_kind():
    rows = [authority(i, citation="") for i in range(1, 5)]
    assert len(remediation_records(DB(rows), "citation_provenance", limit=2)) == 2
    with pytest.raises(ValueError):
        remediation_records(DB(rows), "not_a_real_kind")
    with pytest.raises(ValueError):
        remediation_records(DB(rows), "citation_provenance", limit=501)
