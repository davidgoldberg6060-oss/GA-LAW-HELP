from datetime import date

from app.ingestion.georgia_corpus import (
    AuthorityKind,
    GeorgiaAuthorityRecord,
    select_authority_version,
    validate_record,
)


def record(authority_id: str, start: date, end: date | None = None):
    return GeorgiaAuthorityRecord(
        authority_id=authority_id,
        kind=AuthorityKind.STATUTE,
        citation="O.C.G.A. test",
        title="Test statute",
        text="Verified test authority text.",
        source_url="https://example.ga.gov/test",
        source_name="Georgia official source",
        retrieved_on=date(2026, 9, 25),
        effective_from=start,
        effective_to=end,
    )


def test_selects_version_that_applied_on_case_date():
    old = record("statute-v1", date(2020, 1, 1), date(2024, 12, 31))
    new = record("statute-v2", date(2025, 1, 1))

    assert select_authority_version([old, new], as_of=date(2023, 6, 1)) == old
    assert select_authority_version([old, new], as_of=date(2026, 6, 1)) == new


def test_does_not_use_future_law():
    future = record("future", date(2027, 1, 1))
    assert select_authority_version([future], as_of=date(2026, 9, 25)) is None


def test_rejects_invalid_effective_range():
    bad = record("bad", date(2026, 1, 2), date(2026, 1, 1))
    assert "effective_to cannot precede effective_from" in validate_record(bad)
