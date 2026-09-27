from datetime import datetime, timezone

from app.ingestion.adapters import legal_status_from_official_text


def test_official_source_does_not_imply_current_or_precedential():
    checked = datetime(2026, 9, 27, tzinfo=timezone.utc)
    status = legal_status_from_official_text(
        "Opinion published by the Supreme Court of Georgia.",
        "https://www.gasupreme.us/2026-opinions/",
        checked_at=checked,
    )
    assert status.verification_status == "official"
    assert status.currency_status == "unknown"
    assert status.precedential_status == "unknown"
    assert status.status_checked_at == checked


def test_explicit_negative_treatment_is_recorded():
    status = legal_status_from_official_text(
        "The prior opinion is withdrawn and superseded.",
        "https://www.gaappeals.us/opinions/",
    )
    assert status.currency_status in {"withdrawn", "superseded"}
    assert "withdrawn" in status.negative_treatment
    assert "superseded" in status.negative_treatment


def test_explicit_effective_language_can_establish_currency_not_precedent():
    status = legal_status_from_official_text(
        "These rules are currently effective.",
        "https://georgiacourts.gov/georgia-supreme-court-rules/",
    )
    assert status.currency_status == "current"
    assert status.precedential_status == "unknown"


def test_non_official_source_is_rejected():
    try:
        legal_status_from_official_text("currently effective", "https://example.com/fake-law")
    except (ValueError, PermissionError):
        return
    raise AssertionError("non-official source must be rejected")
