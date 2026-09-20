from dataclasses import dataclass
from enum import Enum

class VerificationStatus(str, Enum):
    VERIFIED_CURRENT = "verified_current"
    VERIFIED_HISTORICAL = "verified_historical"
    SUPERSEDED = "superseded"
    SOURCE_CHANGED = "source_changed"
    NEEDS_REVIEW = "needs_review"

@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    reason: str
    source_sha256: str | None = None
    replacement_external_id: str | None = None

def verify_snapshot(*, stored_hash: str, fetched_hash: str, final_copy: bool = False,
                    replacement_external_id: str | None = None) -> VerificationResult:
    if replacement_external_id:
        return VerificationResult(VerificationStatus.SUPERSEDED,
            "Official source indicates a replacement/substitute version.", fetched_hash,
            replacement_external_id)
    if stored_hash != fetched_hash:
        return VerificationResult(VerificationStatus.SOURCE_CHANGED,
            "Official source content changed after the stored snapshot.", fetched_hash)
    if final_copy:
        return VerificationResult(VerificationStatus.VERIFIED_CURRENT,
            "Hash matches the official final-copy source.", fetched_hash)
    return VerificationResult(VerificationStatus.NEEDS_REVIEW,
        "Hash matches, but final/current authority status still requires confirmation.", fetched_hash)
