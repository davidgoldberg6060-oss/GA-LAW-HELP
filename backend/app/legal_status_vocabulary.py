"""Single vocabulary for stored legal-authority status metadata.

These are every value the ingestion/remediation code can write to
``legal_authorities.currency_status`` and ``legal_authorities.precedential_status``.
``unknown`` is always the conservative default: status is never inferred merely because a
source is official. The database CHECK constraints (model + backend/migrations) use these sets.
"""
from __future__ import annotations

UNKNOWN = "unknown"

#: Explicit adverse treatment detected from official source text (ingestion.adapters) or
#: verified remediation evidence. Any of these blocks use as supporting authority.
NEGATIVE_TREATMENTS = frozenset({"overruled", "vacated", "superseded", "withdrawn", "repealed"})

#: currency_status: unknown, "current" (explicit "currently effective" evidence), or the
#: adverse treatment itself (persistence stores the treatment as the currency status).
CURRENCY_STATUSES = frozenset({UNKNOWN, "current"}) | NEGATIVE_TREATMENTS

#: precedential_status: unknown, "binding" / "nonprecedential" from verified evidence, or an
#: adverse treatment carried over from verified evidence.
PRECEDENTIAL_STATUSES = frozenset({UNKNOWN, "binding", "nonprecedential"}) | NEGATIVE_TREATMENTS


def _normalize(value: str | None, allowed: frozenset[str]) -> str:
    clean = (value or "").strip().lower()
    return clean if clean in allowed else UNKNOWN


def normalize_currency_status(value: str | None) -> str:
    """Lower-case a currency status; blank or unrecognized values become ``unknown``."""
    return _normalize(value, CURRENCY_STATUSES)


def normalize_precedential_status(value: str | None) -> str:
    """Lower-case a precedential status; blank or unrecognized values become ``unknown``."""
    return _normalize(value, PRECEDENTIAL_STATUSES)


def sql_in_list(values: frozenset[str]) -> str:
    return ", ".join(f"'{v}'" for v in sorted(values))
