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


def _gap_summary(rows: list[LegalAuthority], verified: list[LegalAuthority]) -> dict:
    """Describe concrete metadata/verification gaps without guessing missing law."""
    missing_citation = [row for row in rows if not str(row.citation or "").strip()]
    missing_https_source = [row for row in rows if not str(row.source_url or "").startswith("https://")]
    unverified = [row for row in rows if _norm(row.status) not in _VERIFIED]
    verified_missing_status_check = [
        row for row in verified
        if row.status_checked_at is None or not str(row.status_source_url or "").startswith("https://")
    ]
    unknown_currency = [row for row in verified if _norm(row.currency_status) == "unknown"]
    unknown_precedential = [row for row in verified if _norm(row.precedential_status) == "unknown"]
    return {
        "records_missing_citation": len(missing_citation),
        "records_missing_https_source": len(missing_https_source),
        "records_not_verified": len(unverified),
        "verified_missing_status_check": len(verified_missing_status_check),
        "verified_unknown_currency": len(unknown_currency),
        "verified_unknown_precedential_status": len(unknown_precedential),
    }


def _remediation_queue(gaps: dict) -> list[dict]:
    """Turn measured stored-record defects into a deterministic repair queue.

    This prioritizes provenance before legal-status enrichment. It does not infer
    that any record is valid law and does not estimate authorities absent from the
    corpus.
    """
    plan = (
        ("records_missing_https_source", "source_provenance", 10,
         "Attach an HTTPS source URL from the stored source record before the authority can be treated as traceable."),
        ("records_missing_citation", "citation_provenance", 20,
         "Recover the citation from the source record; never synthesize or guess a citation."),
        ("records_not_verified", "verification", 30,
         "Verify against an authoritative stored source before allowing the record to support Georgia-law conclusions."),
        ("verified_missing_status_check", "status_check", 40,
         "Record a dated HTTPS status source before describing current treatment."),
        ("verified_unknown_currency", "currency_status", 50,
         "Determine currency from an authoritative status source; leave unknown when evidence is unavailable."),
        ("verified_unknown_precedential_status", "precedential_status", 60,
         "Determine precedential status from an authoritative source; leave unknown when evidence is unavailable."),
    )
    return [
        {"priority": priority, "kind": kind, "records": int(gaps.get(key, 0)), "action": action}
        for key, kind, priority, action in plan
        if int(gaps.get(key, 0)) > 0
    ]


def corpus_coverage(db: Session, *, jurisdiction: str = "GA") -> dict:
    """Return auditable corpus counts and concrete quality gaps without claiming completeness."""
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
    gaps = _gap_summary(rows, verified)
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
        "quality_gaps": gaps,
        "remediation_queue": _remediation_queue(gaps),
        "completeness_claimed": False,
        "coverage_notice": (
            "Counts describe records currently stored in GA.LAW.HELP. They do not prove that "
            "every Georgia statute, rule, opinion, historical case, or later treatment is present. "
            "Quality gaps and remediation priorities describe stored-record metadata only and must not be interpreted as an estimate of missing Georgia law."
        ),
    }
