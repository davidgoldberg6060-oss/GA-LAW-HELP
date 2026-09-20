import hashlib
from .models import SourceDocument, Snapshot

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def snapshot(doc: SourceDocument) -> Snapshot:
    return Snapshot(
        source_key=doc.source_key,
        url=doc.url,
        sha256=sha256_bytes(doc.body),
        retrieved_at=doc.retrieved_at,
        byte_length=len(doc.body),
        external_id=doc.external_id,
    )

def changed(previous_sha256: str | None, doc: SourceDocument) -> bool:
    return previous_sha256 != sha256_bytes(doc.body)
