"""Evidence-gated application of Georgia corpus remediation work.

Remediation is deliberately separate from discovery. This module never searches
for, infers, or manufactures legal metadata. A caller must supply an authoritative
SourceDocument and, where relevant, the citation published by that source.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import LegalAuthority
from .models import SourceDocument
from .persistence import _merge_status

_VERIFIED = {"verified", "official", "validated", "confirmed"}
_STATUS_KINDS = {"verification", "status_check", "currency_status", "precedential_status"}
_SUPPORTED = {"source_provenance", "citation_provenance", *_STATUS_KINDS}


def _verified(document: SourceDocument) -> bool:
    return str(document.legal_status.verification_status or "").strip().lower() in _VERIFIED


def apply_authoritative_remediation(
    db: Session,
    *,
    authority_id: int,
    kind: str,
    evidence: SourceDocument,
    published_citation: str | None = None,
) -> LegalAuthority:
    """Apply one remediation item when authoritative source evidence is supplied.

    This function does not commit the transaction. Callers can combine evidence
    checks and multiple repairs atomically. Unknown status fields remain unknown.
    """
    if kind not in _SUPPORTED:
        raise ValueError(f"Unsupported remediation kind: {kind}")
    if not evidence.url.startswith("https://"):
        raise ValueError("remediation evidence must use HTTPS")

    authority = db.query(LegalAuthority).filter(LegalAuthority.id == authority_id).one_or_none()
    if authority is None:
        raise ValueError("authority not found")
    if str(authority.jurisdiction or "").upper() != "GA":
        raise ValueError("remediation is restricted to Georgia authorities")

    if kind == "source_provenance":
        authority.source_url = evidence.url
        authority.retrieved_at = evidence.retrieved_at

    elif kind == "citation_provenance":
        citation = str(published_citation or "").strip()
        if not citation:
            raise ValueError("published citation from the authoritative source is required")
        collision = (
            db.query(LegalAuthority)
            .filter(
                LegalAuthority.jurisdiction == authority.jurisdiction,
                LegalAuthority.citation == citation,
                LegalAuthority.id != authority.id,
            )
            .one_or_none()
        )
        if collision is not None:
            raise ValueError("published citation already belongs to another stored authority")
        authority.citation = citation
        authority.source_url = evidence.url
        authority.retrieved_at = evidence.retrieved_at

    else:
        if not _verified(evidence):
            raise ValueError("legal-status remediation requires verified authoritative evidence")
        if kind == "status_check" and (
            evidence.legal_status.status_checked_at is None
            or not str(evidence.legal_status.status_source_url or "").startswith("https://")
        ):
            raise ValueError("status-check remediation requires a dated HTTPS status source")
        if kind == "currency_status" and str(evidence.legal_status.currency_status or "unknown").lower() == "unknown":
            raise ValueError("authoritative evidence does not establish currency status")
        if kind == "precedential_status" and str(evidence.legal_status.precedential_status or "unknown").lower() == "unknown":
            raise ValueError("authoritative evidence does not establish precedential status")
        _merge_status(authority, evidence.legal_status)

    db.flush()
    return authority
