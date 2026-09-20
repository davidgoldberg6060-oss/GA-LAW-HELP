import hashlib, secrets, os
from datetime import timedelta
from sqlalchemy.orm import Session
from . import models

REFRESH_DAYS=int(os.getenv('REFRESH_TOKEN_DAYS','30'))
RESET_MINUTES=int(os.getenv('PASSWORD_RESET_MINUTES','30'))
VERIFY_HOURS=int(os.getenv('EMAIL_VERIFICATION_HOURS','24'))

def _hash(token:str)->str: return hashlib.sha256(token.encode()).hexdigest()

def issue_refresh(db:Session,user_id:int):
    raw=secrets.token_urlsafe(48)
    db.add(models.RefreshToken(user_id=user_id,token_hash=_hash(raw),expires_at=models.utcnow()+timedelta(days=REFRESH_DAYS)))
    return raw

def rotate_refresh(db:Session,raw:str):
    now=models.utcnow(); row=db.query(models.RefreshToken).filter_by(token_hash=_hash(raw)).first()
    if not row or row.expires_at <= now: return None
    if row.revoked_at:
        # Reuse of a rotated token can indicate theft. Revoke the user's remaining sessions.
        revoke_all_user_refresh_tokens(db,row.user_id)
        return None
    row.revoked_at=now
    replacement=issue_refresh(db,row.user_id)
    row.replaced_by_hash=_hash(replacement)
    return row.user_id, replacement

def revoke_refresh(db:Session,raw:str):
    row=db.query(models.RefreshToken).filter_by(token_hash=_hash(raw)).first()
    if not row or row.revoked_at: return False
    row.revoked_at=models.utcnow(); return True

def revoke_all_user_refresh_tokens(db:Session,user_id:int):
    now=models.utcnow()
    rows=db.query(models.RefreshToken).filter_by(user_id=user_id,revoked_at=None).all()
    for row in rows: row.revoked_at=now
    return len(rows)

def issue_reset(db:Session,user_id:int):
    now=models.utcnow()
    for row in db.query(models.PasswordResetToken).filter_by(user_id=user_id,used_at=None).all():
        row.used_at=now
    raw=secrets.token_urlsafe(48)
    db.add(models.PasswordResetToken(user_id=user_id,token_hash=_hash(raw),expires_at=now+timedelta(minutes=RESET_MINUTES)))
    return raw

def consume_reset(db:Session,raw:str):
    now=models.utcnow(); row=db.query(models.PasswordResetToken).filter_by(token_hash=_hash(raw)).first()
    if not row or row.used_at or row.expires_at <= now: return None
    row.used_at=now; return row.user_id

def issue_email_verification(db:Session,user_id:int):
    now=models.utcnow()
    for row in db.query(models.EmailVerificationToken).filter_by(user_id=user_id,used_at=None).all():
        row.used_at=now
    raw=secrets.token_urlsafe(48)
    db.add(models.EmailVerificationToken(user_id=user_id,token_hash=_hash(raw),expires_at=now+timedelta(hours=VERIFY_HOURS)))
    return raw

def consume_email_verification(db:Session,raw:str):
    now=models.utcnow()
    row=db.query(models.EmailVerificationToken).filter_by(token_hash=_hash(raw)).first()
    if not row or row.used_at or row.expires_at <= now: return None
    row.used_at=now
    return row.user_id
