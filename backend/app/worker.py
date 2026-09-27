"""Private evidence worker for GA.LAW.HELP.

The worker performs local integrity processing itself. Provider-dependent media
analysis stays explicitly paused until a reviewed provider is configured; case
files are never uploaded to an unconfigured third party.
"""
import json
import logging
import os
import sys
import time
from datetime import timedelta

from .database import SessionLocal
from .models import AnalysisJob, Evidence, EvidenceFinding, utcnow
from .storage import hash_stored


logger = logging.getLogger("ga_law_help.worker")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), stream=sys.stdout)

LOCAL_JOB_TYPES = {"PROBE_MEDIA"}
PROVIDER_JOB_TYPES = {
    "TRANSCRIBE_DEEP_LISTENING",
    "FRAME_ANALYSIS",
    "REFLECTION_ANALYSIS",
    "OFF_CAMERA_RECONSTRUCTION",
}


class AwaitingProvider(RuntimeError):
    pass


def _log(event: str, **fields) -> None:
    # Structured, privacy-safe operational logs: never include filenames,
    # storage keys, case narratives, transcripts, or secret values.
    logger.info(json.dumps({"event": event, **fields}, sort_keys=True))


def validate_worker_config():
    if os.getenv("ENVIRONMENT", "development").lower() != "production":
        return
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url or database_url.startswith("sqlite") or "sslmode=" not in database_url:
        raise RuntimeError("Worker requires a production PostgreSQL DATABASE_URL with SSL")
    if os.getenv("STORAGE_BACKEND", "local").lower() != "s3":
        raise RuntimeError("Worker requires STORAGE_BACKEND=s3")
    required = ("S3_BUCKET", "S3_ENDPOINT_URL", "AWS_REGION", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Worker S3 configuration is incomplete: " + ", ".join(missing))


def _record_integrity_finding(db, evidence: Evidence, verified: bool) -> None:
    finding = (
        db.query(EvidenceFinding)
        .filter_by(evidence_id=evidence.id, finding_type="INTEGRITY_VERIFICATION")
        .first()
    )
    if finding is None:
        finding = EvidenceFinding(
            evidence_id=evidence.id,
            finding_type="INTEGRITY_VERIFICATION",
            evidence_label="VERIFIED" if verified else "MISMATCH",
            text="",
        )
        db.add(finding)
    finding.evidence_label = "VERIFIED" if verified else "MISMATCH"
    finding.text = (
        "Stored original matches its upload fingerprint and declared byte count."
        if verified
        else "Stored original does not match its upload fingerprint or declared byte count."
    )
    finding.confidence = "HIGH"
    finding.limitations = (
        "Integrity verification confirms file consistency only; it does not establish authenticity, "
        "completeness, authorship, admissibility, or the truth of the file's contents."
    )


def process(db, job: AnalysisJob) -> bool:
    """Process one job without exporting private evidence to an outside site."""
    evidence = db.get(Evidence, job.evidence_id)
    if evidence is None:
        raise RuntimeError("Evidence record is unavailable")

    if job.job_type == "PROBE_MEDIA":
        digest, size = hash_stored(evidence.storage_key)
        verified = digest == evidence.sha256 and size == evidence.size_bytes
        _record_integrity_finding(db, evidence, verified)
        if not verified:
            raise RuntimeError("Stored evidence integrity verification failed")
        evidence.verified_at = utcnow()
        return True

    if job.job_type in PROVIDER_JOB_TYPES:
        raise AwaitingProvider("Reviewed private-analysis provider is not configured")
    raise RuntimeError("Unsupported analysis job type")


def recover_jobs(db) -> int:
    """Recover jobs stranded by the previous worker shell or an interrupted run."""
    recovered = (
        db.query(AnalysisJob)
        .filter(
            AnalysisJob.job_type.in_(LOCAL_JOB_TYPES),
            AnalysisJob.status == "AWAITING_PROVIDER",
            AnalysisJob.error == "Analysis provider not configured",
        )
        .update({"status": "QUEUED", "progress": 0, "error": None}, synchronize_session=False)
    )
    stale_before = utcnow() - timedelta(minutes=int(os.getenv("WORKER_STALE_MINUTES", "30")))
    recovered += (
        db.query(AnalysisJob)
        .filter(AnalysisJob.status == "PROCESSING", AnalysisJob.updated_at < stale_before)
        .update({"status": "QUEUED", "progress": 0, "error": None}, synchronize_session=False)
    )
    db.commit()
    return recovered


def claim_next_job(db):
    job = (
        db.query(AnalysisJob)
        .filter_by(status="QUEUED")
        .order_by(AnalysisJob.id)
        .with_for_update(skip_locked=True)
        .first()
    )
    if job is not None:
        job.status = "PROCESSING"
        job.progress = 5
        job.error = None
        job.updated_at = utcnow()
        db.commit()
        db.refresh(job)
    return job


def finish_job(db, job: AnalysisJob) -> None:
    try:
        completed = process(db, job)
        job.status = "COMPLETE" if completed else "FAILED"
        job.progress = 100 if completed else job.progress
        job.error = None if completed else "Analysis did not complete"
    except AwaitingProvider as exc:
        db.rollback()
        job = db.get(AnalysisJob, job.id)
        job.status = "AWAITING_PROVIDER"
        job.error = str(exc)
    except Exception as exc:
        db.rollback()
        job = db.get(AnalysisJob, job.id)
        job.status = "FAILED"
        job.error = str(exc)[:500]
        _log("job_failed", job_id=job.id, job_type=job.job_type, error_type=type(exc).__name__)
    job.updated_at = utcnow()
    db.commit()
    _log("job_finished", job_id=job.id, job_type=job.job_type, status=job.status)


def run():
    validate_worker_config()
    poll_seconds = max(1, int(os.getenv("WORKER_POLL_SECONDS", "5")))
    heartbeat_seconds = max(15, int(os.getenv("WORKER_HEARTBEAT_SECONDS", "60")))
    last_heartbeat = 0.0

    with SessionLocal() as db:
        recovered = recover_jobs(db)
    _log("worker_started", recovered_jobs=recovered)

    while True:
        now = time.monotonic()
        if now - last_heartbeat >= heartbeat_seconds:
            _log("worker_heartbeat", status="ok")
            last_heartbeat = now

        with SessionLocal() as db:
            job = claim_next_job(db)
            if job is not None:
                finish_job(db, job)
        time.sleep(poll_seconds)


if __name__ == "__main__":
    run()
