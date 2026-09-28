"""Persistence helpers for evidence-backed Georgia legal authority ingestion.

The merge policy is intentionally conservative: unknown or weaker incoming
metadata must not erase a stronger stored determination. Explicit negative
legal treatment always wins because it is unsafe to continue presenting an
authority affirmatively after the official source identifies adverse status.
"""
from __future__ import annotations

from hashlib import sha256

from sqlalchemy.orm import Session

from ..models import AuthorityVersion, LegalAuthority
from .models import LegalStatus, SourceDocument

_VERIFIED = {"verified", "official", "validated", "confirmed"}
_NEGATIVE = {"overruled", "vacated", "superseded", "withdrawn", "repealed"}


def _verified(value: str | None) -> bool:
    return (value or "").strip().lower() in _VERIFIED


def _negative(status: LegalStatus) -> set[str]:
    values = {x.strip().lower() for x in status.negative_treatment if x}
    if status.currency_status.lower() in _NEGATIVE:
        values.add(status.currency_status.lower())
    if status.precedential_status.lower() in _NEGATIVE:
        values.add(status.precedential_status.lower())
    return values


def _merge_status(authority: LegalAuthority, incoming: LegalStatus) -> None:
    """Merge status evidence without downgrading verified stored evidence."""
    incoming_negative = _negative(incoming)
    stored_verified = _verified(authority.status)
    incoming_verified = _verified(incoming.verification_status)

    # Explicit adverse treatment from verified source evidence is safety-critical.
    if incoming_verified and incoming_negative:
        treatment = sorted(incoming_negative)
        authority.currency_status = treatment[0]
        authority.negative_treatment = ", ".join(treatment)
        authority.precedential_status = (
            incoming.precedential_status
            if incoming.precedential_status.lower() in _NEGATIVE
            else authority.precedential_status
        )
        authority.superseding_authority = incoming.superseded_by or authority.superseding_authority
        authority.status_checked_at = incoming.status_checked_at
        authority.status_source_url = incoming.status_source_url
        authority.status = incoming.verification_status.upper()
        return

    if not incoming_verified:
        return

    # Unknown incoming fields never erase known stored determinations.
    if incoming.currency_status.lower() != "unknown":
        authority.currency_status = incoming.currency_status
    if incoming.precedential_status.lower() != "unknown":
        authority.precedential_status = incoming.precedential_status
    if incoming.superseded_by:
        authority.superseding_authority = incoming.superseded_by
    if incoming.negative_treatment:
        authority.negative_treatment = ", ".join(incoming.negative_treatment)

    # Preserve the strongest traceable check. A verified incoming check may
    # replace an older check, but an undated/untraceable one may not.
    if incoming.status_checked_at and incoming.status_source_url and incoming.status_source_url.startswith("https://"):
        if not authority.status_checked_at or incoming.status_checked_at >= authority.status_checked_at:
            authority.status_checked_at = incoming.status_checked_at
            authority.status_source_url = incoming.status_source_url
    if not stored_verified or incoming_verified:
        authority.status = incoming.verification_status.upper()


def upsert_authority_document(
    db: Session,
    *,
    document: SourceDocument,
    jurisdiction: str,
    authority_type: str,
    citation: str,
) -> LegalAuthority:
    """Upsert an authority and immutable content version from an ingested document."""
    if not citation.strip():
        raise ValueError("citation is required; fabricated/blank authority identifiers are not permitted")
    if not document.url.startswith("https://"):
        raise ValueError("authority source must use HTTPS")

    authority = (
        db.query(LegalAuthority)
        .filter(LegalAuthority.jurisdiction == jurisdiction, LegalAuthority.citation == citation)
        .one_or_none()
    )
    text = document.extracted_text if document.extracted_text is not None else document.body.decode("utf-8", errors="replace")
    digest = sha256(document.body).hexdigest()

    if authority is None:
        authority = LegalAuthority(
            jurisdiction=jurisdiction,
            authority_type=authority_type,
            citation=citation,
            title=document.title,
            text=text,
            status="UNVERIFIED",
            source_url=document.url,
            retrieved_at=document.retrieved_at,
            currency_status="unknown",
            precedential_status="unknown",
        )
        db.add(authority)
        db.flush()
    else:
        authority.title = document.title or authority.title
        authority.text = text
        authority.source_url = document.url
        authority.retrieved_at = document.retrieved_at

    _merge_status(authority, document.legal_status)

    existing_version = (
        db.query(AuthorityVersion)
        .filter(
            AuthorityVersion.authority_id == authority.id,
            AuthorityVersion.content_sha256 == digest,
        )
        .one_or_none()
    )
    if existing_version is None:
        db.add(
            AuthorityVersion(
                authority_id=authority.id,
                version_label=document.external_id,
                text=text,
                effective_from=document.effective_at.date() if document.effective_at else None,
                source_url=document.url,
                content_sha256=digest,
                verification_status=document.legal_status.verification_status.upper(),
                retrieved_at=document.retrieved_at,
            )
        )

    db.flush()
    return authority
