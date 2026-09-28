from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion.models import LegalStatus, SourceDocument
from app.ingestion.remediation_apply import apply_authoritative_remediation
from app.models import LegalAuthority


def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def evidence(*, url="https://www.gasupreme.us/opinion", verification="VERIFIED", currency="unknown", precedent="unknown", checked=True):
    now = datetime.now(timezone.utc)
    status = LegalStatus(
        verification_status=verification,
        currency_status=currency,
        precedential_status=precedent,
        status_checked_at=now if checked else None,
        status_source_url="https://www.gasupreme.us/status" if checked else None,
    )
    return SourceDocument(
        source_key="ga_supreme_opinions",
        url=url,
        title="Official authority",
        body=b"official source text",
        retrieved_at=now,
        legal_status=status,
    )


def stored(db, *, citation=""):
    row = LegalAuthority(
        jurisdiction="GA", authority_type="case", citation=citation,
        title="Stored authority", text="text", status="UNVERIFIED",
        source_url="", currency_status="unknown", precedential_status="unknown",
    )
    db.add(row); db.flush(); return row


def test_citation_repair_requires_published_authoritative_citation():
    db = db_session(); row = stored(db)
    with pytest.raises(ValueError, match="published citation"):
        apply_authoritative_remediation(db, authority_id=row.id, kind="citation_provenance", evidence=evidence())
    repaired = apply_authoritative_remediation(db, authority_id=row.id, kind="citation_provenance", evidence=evidence(), published_citation="321 Ga. 123")
    assert repaired.citation == "321 Ga. 123"
    assert repaired.source_url.startswith("https://")


def test_status_repair_rejects_unverified_or_unknown_evidence():
    db = db_session(); row = stored(db, citation="321 Ga. 123")
    with pytest.raises(ValueError, match="verified authoritative evidence"):
        apply_authoritative_remediation(db, authority_id=row.id, kind="currency_status", evidence=evidence(verification="UNVERIFIED", currency="current"))
    with pytest.raises(ValueError, match="does not establish currency"):
        apply_authoritative_remediation(db, authority_id=row.id, kind="currency_status", evidence=evidence())


def test_verified_status_evidence_updates_only_established_fields():
    db = db_session(); row = stored(db, citation="321 Ga. 123")
    repaired = apply_authoritative_remediation(db, authority_id=row.id, kind="currency_status", evidence=evidence(currency="current"))
    assert repaired.currency_status == "current"
    assert repaired.precedential_status == "unknown"
    assert repaired.status == "VERIFIED"


def test_remediation_rejects_insecure_source():
    db = db_session(); row = stored(db)
    with pytest.raises(ValueError, match="HTTPS"):
        apply_authoritative_remediation(db, authority_id=row.id, kind="source_provenance", evidence=evidence(url="http://example.test/opinion"))
