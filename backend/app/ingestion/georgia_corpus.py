"""Georgia legal corpus normalization and temporal authority selection.

This module keeps ingestion source-agnostic while preserving the metadata needed
for date-correct legal retrieval. Network/source adapters should fetch only from
approved authoritative sources and pass normalized records here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Iterable


class AuthorityKind(str, Enum):
    STATUTE = "statute"
    CASE = "case"
    COURT_RULE = "court_rule"
    CONSTITUTION = "constitution"
    REGULATION = "regulation"


@dataclass(frozen=True, slots=True)
class GeorgiaAuthorityRecord:
    authority_id: str
    kind: AuthorityKind
    citation: str
    title: str
    text: str
    source_url: str
    source_name: str
    retrieved_on: date
    effective_from: date | None = None
    effective_to: date | None = None
    decision_date: date | None = None
    supersedes_id: str | None = None

    def applies_on(self, as_of: date) -> bool:
        """Return whether this version may be used for the requested legal date."""
        start = self.effective_from or self.decision_date
        if start is not None and as_of < start:
            return False
        if self.effective_to is not None and as_of > self.effective_to:
            return False
        return True


def select_authority_version(
    records: Iterable[GeorgiaAuthorityRecord], *, as_of: date
) -> GeorgiaAuthorityRecord | None:
    """Select the newest applicable version without silently using future law."""
    applicable = [record for record in records if record.applies_on(as_of)]
    if not applicable:
        return None

    def temporal_key(record: GeorgiaAuthorityRecord) -> tuple[date, date]:
        legal_date = record.effective_from or record.decision_date or date.min
        return legal_date, record.retrieved_on

    return max(applicable, key=temporal_key)


def validate_record(record: GeorgiaAuthorityRecord) -> list[str]:
    """Return ingestion errors; an empty list means the record is acceptable."""
    errors: list[str] = []
    if not record.authority_id.strip():
        errors.append("authority_id is required")
    if not record.citation.strip():
        errors.append("citation is required")
    if not record.text.strip():
        errors.append("authority text is required")
    if not record.source_url.startswith("https://"):
        errors.append("source_url must use https")
    if not record.source_name.strip():
        errors.append("source_name is required")
    if (
        record.effective_from is not None
        and record.effective_to is not None
        and record.effective_to < record.effective_from
    ):
        errors.append("effective_to cannot precede effective_from")
    return errors
