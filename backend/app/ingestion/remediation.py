"""Record-level remediation planning for the internal Georgia legal corpus.

This module selects stored records that need provenance or legal-status work. It
never repairs a record by inference and never manufactures citations/status.
Actual remediation must be backed by an authoritative source document.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import LegalAuthority

_VERIFIED = {"verified", "official", "validated", "confirmed"}


def _norm(value: object) -> str:
    return str(value or "unknown").strip().lower() or "unknown"


def _needs(row: LegalAuthority, kind: str) -> bool:
    verified = _norm(row.status) in _VERIFIED
    if kind == "source_provenance":
        return not str(row.source_url or "").startswith("https://")
    if kind == "citation_provenance":
        return not str(row.citation or "").strip()
    if kind == "verification":
        return not verified
    if kind == "status_check":
        return verified and (row.status_checked_at is None or not str(row.status_source_url or "").startswith("https://"))
    if kind == "currency_status":
        return verified and _norm(row.currency_status) == "unknown"
    if kind == "precedential_status":
        return verified and _norm(row.precedential_status) == "unknown"
    raise ValueError(f"Unsupported remediation kind: {kind}")


def remediation_records(db: Session, kind: str, *, jurisdiction: str = "GA", limit: int = 100) -> list[dict]:
    """Return a bounded, deterministic list of stored records needing `kind` work.

    The returned objects are work descriptors, not repaired authorities. No legal
    field is changed and no missing value is guessed.
    """
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")
    rows = db.query(LegalAuthority).filter(LegalAuthority.jurisdiction == jurisdiction).all()
    selected = sorted((row for row in rows if _needs(row, kind)), key=lambda row: int(row.id))[:limit]
    return [
        {
            "authority_id": row.id,
            "kind": kind,
            "citation": row.citation or None,
            "title": row.title or None,
            "source_url": row.source_url or None,
            "verification_status": row.status,
            "currency_status": row.currency_status,
            "precedential_status": row.precedential_status,
            "requires_authoritative_source": True,
        }
        for row in selected
    ]
