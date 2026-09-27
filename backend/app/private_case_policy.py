"""Security invariants for private user case workspaces.

Private case records are never part of the public/legal-authority corpus. All access
must be authenticated and ownership-scoped. Storage keys are opaque server-side
identifiers and must never be exposed as public object URLs.
"""
import os
import uuid
from dataclasses import dataclass
from typing import Iterable


PRIVATE_CASE_RESOURCE_TYPES = frozenset({
    "case",
    "case_note",
    "timeline_event",
    "evidence",
    "evidence_finding",
    "analysis_job",
    "case_authority_link",
})

PUBLIC_CORPUS_RESOURCE_TYPES = frozenset({
    "legal_authority",
    "authority_version",
    "legal_source",
})


@dataclass(frozen=True)
class PrivateCasePolicy:
    authenticated: bool
    owner_id: int
    requester_id: int

    @property
    def allowed(self) -> bool:
        return self.authenticated and self.owner_id == self.requester_id


def require_private_case_owner(*, owner_id: int, requester_id: int, authenticated: bool = True) -> None:
    """Fail closed unless the authenticated requester owns the case workspace."""
    if not PrivateCasePolicy(authenticated, owner_id, requester_id).allowed:
        # Callers translate this to the API's non-enumerating 404 response.
        raise PermissionError("private case workspace access denied")


def assert_private_resources_not_public(resource_types: Iterable[str]) -> None:
    """Guard ingestion/export code from mixing private case data into public corpus."""
    overlap = PRIVATE_CASE_RESOURCE_TYPES.intersection(resource_types)
    if overlap:
        raise ValueError("private case resources cannot enter public corpus: " + ", ".join(sorted(overlap)))


def private_storage_prefix(user_id: int, case_id: int) -> str:
    """Canonical namespace for private evidence objects."""
    if user_id <= 0 or case_id <= 0:
        raise ValueError("user_id and case_id must be positive")
    return f"private/users/{user_id}/cases/{case_id}"


def private_evidence_key(user_id: int, case_id: int, filename: str, *, object_id: str | None = None) -> str:
    """Create a server-side evidence key inside the canonical private namespace."""
    safe_name = os.path.basename(filename or "evidence")
    token = object_id or uuid.uuid4().hex
    if not token or "/" in token or "\\" in token:
        raise ValueError("object_id must be a single opaque path segment")
    return f"{private_storage_prefix(user_id, case_id)}/{token}_{safe_name}"
