from dataclasses import dataclass
from datetime import date
from typing import Iterable

@dataclass(frozen=True)
class AuthorityVersion:
    id: str
    effective_from: date
    effective_to: date | None
    text_hash: str
    status: str

def version_on(versions: Iterable[AuthorityVersion], when: date) -> AuthorityVersion | None:
    candidates = [v for v in versions if v.effective_from <= when and (v.effective_to is None or when < v.effective_to)]
    if not candidates:
        return None
    return max(candidates, key=lambda v: v.effective_from)
