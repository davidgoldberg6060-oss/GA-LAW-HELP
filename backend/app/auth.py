import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db
from . import models

SECRET = os.getenv('JWT_SECRET', 'CHANGE-ME-IN-PRODUCTION')
ALGORITHM = 'HS256'
ACCESS_MINUTES = int(os.getenv('ACCESS_TOKEN_MINUTES', '60'))
ISSUER = os.getenv('JWT_ISSUER', 'ga-law-help')
AUDIENCE = os.getenv('JWT_AUDIENCE', 'ga-law-help-android')
pwd = CryptContext(schemes=['argon2', 'bcrypt'], deprecated='auto')
oauth2 = OAuth2PasswordBearer(tokenUrl='/auth/login')

def hash_password(value: str) -> str: return pwd.hash(value)
def verify_password(value: str, hashed: str) -> bool: return pwd.verify(value, hashed)
def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    import secrets
    return jwt.encode({'sub': str(user_id), 'iat': now, 'nbf': now, 'exp': now + timedelta(minutes=ACCESS_MINUTES),
        'iss': ISSUER, 'aud': AUDIENCE, 'jti': secrets.token_urlsafe(16)}, SECRET, algorithm=ALGORITHM)

def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM], audience=AUDIENCE, issuer=ISSUER); uid = int(payload['sub'])
    except Exception:
        raise HTTPException(401, 'Invalid or expired token', headers={'WWW-Authenticate':'Bearer'})
    user = db.get(models.User, uid)
    if not user or not user.is_active: raise HTTPException(401, 'User is unavailable')
    return user

def require_paid(user: models.User = Depends(current_user)):
    if user.role not in ('paid','admin'):
        raise HTTPException(403, 'Paid membership required')
    return user

def require_admin(user: models.User = Depends(current_user)):
    if user.role != 'admin':
        raise HTTPException(403, 'Administrator access required')
    return user

def owned_case(case_id: int, user: models.User, db: Session):
    case = db.get(models.Case, case_id)
    if not case or case.owner_id != user.id: raise HTTPException(404, 'Case not found')
    return case
