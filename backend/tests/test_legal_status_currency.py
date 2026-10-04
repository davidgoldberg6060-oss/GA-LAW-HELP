from datetime import datetime, timezone

from app.ingestion.models import LegalStatus


def verified_current(**overrides) -> LegalStatus:
    values = {
        "verification_status": "verified",
        "currency_status": "current",
        "precedential_status": "binding",
        "status_checked_at": datetime.now(timezone.utc),
        "status_source_url": "https://www.gasupreme.us/official-status",
    }
    values.update(overrides)
    return LegalStatus(**values)


def test_current_authority_requires_all_traceability_fields():
    assert verified_current().usable_as_current_authority is True
    assert verified_current(status_checked_at=None).usable_as_current_authority is False
    assert verified_current(status_source_url=None).usable_as_current_authority is False
    assert verified_current(status_source_url="http://example.com/status").usable_as_current_authority is False


def test_unverified_or_unknown_currency_is_not_current_authority():
    assert verified_current(verification_status="unverified").usable_as_current_authority is False
    assert verified_current(currency_status="unknown").usable_as_current_authority is False


def test_negative_precedential_status_blocks_current_authority():
    for status in ("overruled", "vacated", "superseded", "withdrawn", "repealed"):
        assert verified_current(precedential_status=status).usable_as_current_authority is False


def test_status_comparisons_are_case_insensitive():
    assert verified_current(
        verification_status="VERIFIED",
        currency_status="CURRENT",
        precedential_status="BINDING",
    ).usable_as_current_authority is True
