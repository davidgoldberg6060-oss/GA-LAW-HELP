from datetime import datetime, timezone

from backend.app.ingestion.models import LegalStatus
from backend.app.ingestion.persistence import _merge_status


class AuthorityStub:
    status = "OFFICIAL"
    currency_status = "current"
    precedential_status = "binding"
    status_checked_at = datetime(2026, 9, 1, tzinfo=timezone.utc)
    status_source_url = "https://www.gasupreme.us/status"
    superseding_authority = None
    negative_treatment = None


def test_unknown_incoming_status_does_not_erase_known_status():
    authority = AuthorityStub()
    _merge_status(authority, LegalStatus(verification_status="official"))
    assert authority.currency_status == "current"
    assert authority.precedential_status == "binding"
    assert authority.status_source_url == "https://www.gasupreme.us/status"


def test_verified_negative_treatment_overrides_prior_current_status():
    authority = AuthorityStub()
    checked = datetime(2026, 9, 27, tzinfo=timezone.utc)
    _merge_status(
        authority,
        LegalStatus(
            verification_status="official",
            currency_status="overruled",
            status_checked_at=checked,
            status_source_url="https://www.gasupreme.us/opinion-status",
            negative_treatment=("overruled",),
        ),
    )
    assert authority.currency_status == "overruled"
    assert authority.negative_treatment == "overruled"
    assert authority.status_checked_at == checked


def test_unverified_negative_claim_cannot_poison_stored_authority():
    authority = AuthorityStub()
    _merge_status(
        authority,
        LegalStatus(
            verification_status="unverified",
            currency_status="overruled",
            negative_treatment=("overruled",),
        ),
    )
    assert authority.currency_status == "current"
    assert authority.negative_treatment is None


def test_older_status_check_cannot_replace_newer_traceable_check():
    authority = AuthorityStub()
    _merge_status(
        authority,
        LegalStatus(
            verification_status="official",
            currency_status="current",
            status_checked_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
            status_source_url="https://www.legis.ga.gov/older-status",
        ),
    )
    assert authority.status_source_url == "https://www.gasupreme.us/status"
