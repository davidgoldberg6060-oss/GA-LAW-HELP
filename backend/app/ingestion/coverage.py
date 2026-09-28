"""Coverage reporting for the internal Georgia legal corpus.

This module measures what is actually stored. It never estimates missing
Georgia authorities and never turns an unverified record into verified law.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import LegalAuthority

_VERIFIED = {"verified", "official", "validated", "confirmed"}
_NEGATIVE = {"overruled", "vacated", "superseded", "withdrawn", "repealed"}


def _norm(value: object) -> str:
    return str(value or "unknown").strip().lower() or "unknown"


def corpus_coverage(db: Session, *, jurisdiction: str = "GA") -> dict:
    """Return auditable corpus counts without claiming completeness."""
    rows = db.query(LegalAuthority).filter(LegalAuthority.jurisdiction == jurisdiction).all()
    by_type = Counter(_norm(row.authority_type) for row in rows)
    by_status = Counter(_norm(row.status) for row in rows)
    verified = [row for row in rows if _norm(row.status) in _VERIFIED]
    negative = [
        row for row in rows
        if _norm(row.currency_status) in _NEGATIVE
        or _norm(row.precedential_status) in _NEGATIVE
        or any(token in _NEGATIVE for token in (_norm(row.negative_treatment).replace(",", " ").split()))
    ]
    traceable = [
        row for row in verified
        if bool((row.citation or "").strip()) and str(row.source_url or "").startswith("https://")
    ]
    status_checked = [
        row for row in verified
        if row.status_checked_at is not None and str(row.status_source_url or "").startswith("https://")
    ]
    return {
        "jurisdiction": jurisdiction,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_authorities": len(rows),
        "verified_authorities": len(verified),
        "traceable_verified_authorities": len(traceable),
        "verified_with_status_check": len(status_checked),
        "negative_treatment_records": len(negative),
        "by_authority_type": dict(sorted(by_type.items())),
        "by_verification_status": dict(sorted(by_status.items())),
        "completeness_claimed": False,
        "coverage_notice": (
            "Counts describe records currently stored in GA.LAW.HELP. They do not prove that "
            "every Georgia statute, rule, opinion, historical case, or later treatment is present."
        ),
    }
