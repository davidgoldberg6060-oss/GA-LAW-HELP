from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# These fields describe what the ingestion source actually establishes. Unknown
# values stay unknown; ingestion must never infer current/binding status merely
# because a document came from an official website.
@dataclass(frozen=True)
class LegalStatus:
    verification_status: str = "unverified"
    currency_status: str = "unknown"
    precedential_status: str = "unknown"
    status_checked_at: Optional[datetime] = None
    status_source_url: Optional[str] = None
    superseded_by: Optional[str] = None
    negative_treatment: tuple[str, ...] = ()

    @property
    def usable_as_current_authority(self) -> bool:
        return (
            self.verification_status.lower() in {"verified", "official", "validated", "confirmed"}
            and self.currency_status.lower() == "current"
            and self.precedential_status.lower() not in {"overruled", "vacated", "superseded", "withdrawn", "repealed"}
            and bool(self.status_checked_at)
            and bool(self.status_source_url and self.status_source_url.startswith("https://"))
        )

@dataclass(frozen=True)
class SourceDocument:
    source_key: str
    url: str
    title: str
    body: bytes
    retrieved_at: datetime
    published_at: Optional[datetime] = None
    effective_at: Optional[datetime] = None
    external_id: Optional[str] = None
    content_type: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    legal_status: LegalStatus = field(default_factory=LegalStatus)

@dataclass(frozen=True)
class Snapshot:
    source_key: str
    url: str
    sha256: str
    retrieved_at: datetime
    byte_length: int
    external_id: Optional[str]
