from dataclasses import dataclass
from datetime import datetime, timezone
from .models import SourceDocument
from .provenance import sha256_bytes

@dataclass
class UpdateDecision:
    action: str
    sha256: str
    checked_at: datetime


def decide(previous_hash: str | None, body: bytes) -> UpdateDecision:
    h = sha256_bytes(body)
    return UpdateDecision(
        action="ingest_new_version" if previous_hash != h else "no_change",
        sha256=h,
        checked_at=datetime.now(timezone.utc),
    )
