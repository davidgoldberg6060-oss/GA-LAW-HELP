from datetime import datetime, timezone

import pytest

from app.ingestion.models import LegalStatus, SourceDocument
from app.ingestion.remediation_batch import run_remediation_batch
from app.models import LegalAuthority


def _evidence(*, citation_status="verified"):
    return SourceDocument(
        source_key="test-authoritative-source",
        url="https://example.ga.gov/authority",
        title="Authoritative source",
        text="source text",
        retrieved_at=datetime.now(timezone.utc),
        legal_status=LegalStatus(verification_status=citation_status),
    )


def test_batch_skips_records_without_authoritative_evidence(db):
    row = LegalAuthority(jurisdiction="GA", authority_type="case", title="Missing citation", citation="", status="unverified")
    db.add(row); db.flush()
    result = run_remediation_batch(db, kind="citation_provenance", evidence_loader=lambda item: None)
    assert result.selected >= 1
    assert result.applied == 0
    assert result.skipped_no_evidence >= 1
    db.refresh(row)
    assert not row.citation


def test_batch_applies_published_citation_from_supplied_evidence(db):
    row = LegalAuthority(jurisdiction="GA", authority_type="case", title="Missing citation", citation="", status="unverified")
    db.add(row); db.flush()
    target_id = row.id

    def loader(item):
        if item["authority_id"] == target_id:
            return _evidence(), "321 Ga. 456"
        return None

    result = run_remediation_batch(db, kind="citation_provenance", evidence_loader=loader)
    assert result.applied == 1
    db.refresh(row)
    assert row.citation == "321 Ga. 456"
    assert row.source_url == "https://example.ga.gov/authority"


def test_batch_isolates_bad_evidence_and_keeps_other_repairs(db):
    first = LegalAuthority(jurisdiction="GA", authority_type="case", title="First", citation="", status="unverified")
    second = LegalAuthority(jurisdiction="GA", authority_type="case", title="Second", citation="", status="unverified")
    db.add_all([first, second]); db.flush()

    def loader(item):
        if item["authority_id"] == first.id:
            bad = _evidence(); bad.url = "http://insecure.example/authority"
            return bad, "100 Ga. 1"
        if item["authority_id"] == second.id:
            return _evidence(), "100 Ga. 2"
        return None

    result = run_remediation_batch(db, kind="citation_provenance", evidence_loader=loader)
    assert result.failed == 1
    assert result.applied == 1
    db.refresh(first); db.refresh(second)
    assert not first.citation
    assert second.citation == "100 Ga. 2"


def test_batch_rejects_non_georgia_automation(db):
    with pytest.raises(ValueError, match="restricted to Georgia"):
        run_remediation_batch(db, kind="verification", jurisdiction="FL", evidence_loader=lambda item: None)
