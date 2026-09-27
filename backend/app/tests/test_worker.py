import hashlib
from types import SimpleNamespace

import pytest

from app import worker


class FakeQuery:
    def __init__(self, finding=None):
        self.finding = finding

    def filter_by(self, **_kwargs):
        return self

    def first(self):
        return self.finding


class FakeDB:
    def __init__(self, evidence, finding=None):
        self.evidence = evidence
        self.finding = finding
        self.added = []

    def get(self, model, _id):
        if model is worker.Evidence:
            return self.evidence
        return None

    def query(self, model):
        assert model is worker.EvidenceFinding
        return FakeQuery(self.finding)

    def add(self, value):
        self.added.append(value)


def evidence_for(payload=b"private case file"):
    return SimpleNamespace(
        id=7,
        storage_key="private/7/file",
        sha256=hashlib.sha256(payload).hexdigest(),
        size_bytes=len(payload),
        verified_at=None,
    )


def test_probe_media_completes_locally_and_records_limited_finding(monkeypatch):
    payload = b"private case file"
    evidence = evidence_for(payload)
    db = FakeDB(evidence)
    monkeypatch.setattr(worker, "hash_stored", lambda _key: (hashlib.sha256(payload).hexdigest(), len(payload)))
    job = SimpleNamespace(evidence_id=evidence.id, job_type="PROBE_MEDIA")

    assert worker.process(db, job) is True
    assert evidence.verified_at is not None
    assert db.added[0].evidence_label == "VERIFIED"
    assert "does not establish authenticity" in db.added[0].limitations


def test_probe_media_fails_closed_on_hash_mismatch(monkeypatch):
    evidence = evidence_for()
    db = FakeDB(evidence)
    monkeypatch.setattr(worker, "hash_stored", lambda _key: ("0" * 64, evidence.size_bytes))
    job = SimpleNamespace(evidence_id=evidence.id, job_type="PROBE_MEDIA")

    with pytest.raises(RuntimeError, match="integrity verification failed"):
        worker.process(db, job)
    assert evidence.verified_at is None
    assert db.added[0].evidence_label == "MISMATCH"


def test_private_provider_jobs_are_paused_not_faked():
    evidence = evidence_for()
    db = FakeDB(evidence)
    job = SimpleNamespace(evidence_id=evidence.id, job_type="TRANSCRIBE_DEEP_LISTENING")

    with pytest.raises(worker.AwaitingProvider, match="not configured"):
        worker.process(db, job)
