"""Select the version of an authority that applied on a given legal date.

Ranges are half-open: a version applies on ``when`` if ``start <= when < effective_to``.
``start`` is ``effective_from`` (statutes, rules) or, for opinions that have no effective date,
the ``decision_date``. A version whose start is unknown is never selected: we cannot show that
it was in force on the requested date, and future law must never be used silently.
(Date-versioning ideas folded in from PR #59.)
"""
from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class AuthorityVersion:
    id: str
    effective_from: date | None
    effective_to: date | None
    text_hash: str
    status: str
    decision_date: date | None = None
    retrieved_on: date | None = None

    @property
    def start(self) -> date | None:
        return self.effective_from or self.decision_date

    def applies_on(self, when: date) -> bool:
        start = self.start
        if start is None or when < start:
            return False
        return self.effective_to is None or when < self.effective_to


def version_on(versions: Iterable[AuthorityVersion], when: date) -> AuthorityVersion | None:
    """Newest version in force on ``when``; ties go to the most recently retrieved copy."""
    candidates = [v for v in versions if v.applies_on(when)]
    if not candidates:
        return None
    return max(candidates, key=lambda v: (v.start, v.retrieved_on or date.min))


def validate_version(version: AuthorityVersion) -> list[str]:
    """Ingestion errors for a version's date metadata; empty means acceptable."""
    errors: list[str] = []
    if not version.id.strip():
        errors.append("version id is required")
    if not version.text_hash.strip():
        errors.append("text_hash is required")
    if version.start is None:
        errors.append("effective_from or decision_date is required")
    if version.effective_from and version.effective_to and version.effective_to <= version.effective_from:
        errors.append("effective_to must be after effective_from")
    return errors
