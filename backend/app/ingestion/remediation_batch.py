"""Transaction-safe coordination for Georgia corpus remediation batches.

This layer joins deterministic remediation selection to evidence-gated application.
It never discovers legal facts and never manufactures missing authority metadata.
Evidence must be supplied by an authoritative-source acquisition job.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy.orm import Session

from .models import SourceDocument
from .remediation import remediation_records
from .remediation_apply import apply_authoritative_remediation

EvidenceLoader = Callable[[dict], tuple[SourceDocument, str | None] | None]


@dataclass(frozen=True)
class BatchResult:
    kind: str
    selected: int
    applied: int
    skipped_no_evidence: int
    failed: int
    failures: tuple[dict, ...]


def run_remediation_batch(
    db: Session,
    *,
    kind: str,
    evidence_loader: EvidenceLoader,
    jurisdiction: str = "GA",
    limit: int = 100,
) -> BatchResult:
    """Apply a bounded remediation batch using externally acquired evidence.

    Each authority is isolated by a SAVEPOINT so one malformed source cannot undo
    other valid repairs. This function flushes but does not commit the outer
    transaction; the job runner retains control over the final commit/rollback.
    """
    if jurisdiction.upper() != "GA":
        raise ValueError("automated remediation batches are restricted to Georgia")

    work = remediation_records(db, kind, jurisdiction="GA", limit=limit)
    applied = skipped = failed = 0
    failures: list[dict] = []

    for item in work:
        loaded = evidence_loader(dict(item))
        if loaded is None:
            skipped += 1
            continue
        evidence, published_citation = loaded
        try:
            with db.begin_nested():
                apply_authoritative_remediation(
                    db,
                    authority_id=int(item["authority_id"]),
                    kind=kind,
                    evidence=evidence,
                    published_citation=published_citation,
                )
            applied += 1
        except (ValueError, TypeError) as exc:
            failed += 1
            failures.append({
                "authority_id": item["authority_id"],
                "kind": kind,
                "error": str(exc),
            })

    return BatchResult(
        kind=kind,
        selected=len(work),
        applied=applied,
        skipped_no_evidence=skipped,
        failed=failed,
        failures=tuple(failures),
    )
