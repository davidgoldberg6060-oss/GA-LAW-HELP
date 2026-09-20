from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

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

@dataclass(frozen=True)
class Snapshot:
    source_key: str
    url: str
    sha256: str
    retrieved_at: datetime
    byte_length: int
    external_id: Optional[str]
