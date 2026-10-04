from datetime import date

from app.services.law_at_time import AuthorityVersion, validate_version, version_on


def v(id, start, end=None, *, decision=None, retrieved=None, effective=True):
    return AuthorityVersion(id=id, effective_from=start if effective else None, effective_to=end,
                            text_hash="h-" + id, status="OFFICIAL", decision_date=decision, retrieved_on=retrieved)


def test_selects_version_that_applied_on_the_case_date():
    old = v("v1", date(2020, 1, 1), date(2025, 1, 1))
    new = v("v2", date(2025, 1, 1))
    assert version_on([old, new], date(2023, 6, 1)) == old
    assert version_on([old, new], date(2024, 12, 31)) == old
    assert version_on([old, new], date(2025, 1, 1)) == new  # half-open range


def test_never_uses_future_law_or_versions_with_unknown_start():
    assert version_on([v("future", date(2027, 1, 1))], date(2026, 9, 25)) is None
    assert version_on([v("undated", None, effective=False)], date(2026, 9, 25)) is None


def test_opinions_fall_back_to_decision_date():
    opinion = v("op", None, decision=date(2024, 3, 5), effective=False)
    assert version_on([opinion], date(2024, 3, 4)) is None
    assert version_on([opinion], date(2024, 3, 5)) == opinion


def test_ties_go_to_the_most_recently_retrieved_copy():
    first = v("a", date(2025, 1, 1), retrieved=date(2025, 2, 1))
    second = v("b", date(2025, 1, 1), retrieved=date(2026, 9, 1))
    assert version_on([second, first], date(2026, 1, 1)) == second


def test_validate_version_rejects_bad_ranges_and_missing_dates():
    assert validate_version(v("ok", date(2025, 1, 1), date(2026, 1, 1))) == []
    assert "effective_to must be after effective_from" in validate_version(v("bad", date(2026, 1, 2), date(2026, 1, 1)))
    assert validate_version(v("op", None, decision=date(2024, 1, 1), effective=False)) == []
    assert "effective_from or decision_date is required" in validate_version(v("none", None, effective=False))
