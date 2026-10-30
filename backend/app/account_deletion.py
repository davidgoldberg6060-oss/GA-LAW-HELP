"""Permanent deletion of a user's account and all of their private data (Google Play requirement)."""
import logging

from sqlalchemy.orm import Session

from . import models
from .storage import delete_stored, delete_upload_sessions

log = logging.getLogger(__name__)
CONFIRM_WORD = "DELETE"


def delete_account(db: Session, user: models.User) -> dict:
    """Delete the user's cases, notes, timeline, evidence (files and rows), analyses, sessions and tokens, then the user.

    Audit rows that point at the user are removed; one anonymous ACCOUNT_DELETED row is kept.
    """
    uid = user.id
    case_ids = [row[0] for row in db.query(models.Case.id).filter(models.Case.owner_id == uid).all()]
    files_removed = 0
    if case_ids:
        evidence = db.query(models.Evidence).filter(models.Evidence.case_id.in_(case_ids)).all()
        ev_ids = [e.id for e in evidence]
        for e in evidence:
            try:
                delete_stored(e.storage_key)
                files_removed += 1
            except Exception:  # keep deleting rows; a stray object is logged for manual cleanup
                log.warning("account deletion: could not remove stored evidence id=%s", e.id)
        if ev_ids:
            db.query(models.EvidenceFinding).filter(models.EvidenceFinding.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
            db.query(models.AnalysisJob).filter(models.AnalysisJob.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
            db.query(models.Evidence).filter(models.Evidence.id.in_(ev_ids)).delete(synchronize_session=False)
        for model in (models.TimelineEvent, models.IssueAnalysis, models.CaseAuthorityLink, models.CaseNote, models.UploadSession):
            db.query(model).filter(model.case_id.in_(case_ids)).delete(synchronize_session=False)
        for cid in case_ids:
            delete_upload_sessions(uid, cid)
    db.query(models.CaseNote).filter(models.CaseNote.owner_id == uid).delete(synchronize_session=False)
    db.query(models.UploadSession).filter(models.UploadSession.user_id == uid).delete(synchronize_session=False)
    if case_ids:
        db.query(models.Case).filter(models.Case.id.in_(case_ids)).delete(synchronize_session=False)
    for model in (models.RefreshToken, models.PasswordResetToken, models.EmailVerificationToken):
        db.query(model).filter(model.user_id == uid).delete(synchronize_session=False)
    db.query(models.AuditLog).filter(models.AuditLog.user_id == uid).delete(synchronize_session=False)
    db.query(models.User).filter(models.User.id == uid).delete(synchronize_session=False)
    db.add(models.AuditLog(user_id=None, action="ACCOUNT_DELETED", object_type="user", object_id=None))
    db.commit()
    return {"deleted": True, "cases_deleted": len(case_ids), "files_deleted": files_removed}
