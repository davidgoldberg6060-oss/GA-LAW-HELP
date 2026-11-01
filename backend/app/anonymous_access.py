"""No-login access: anonymous device identities and daily caps on AI-backed endpoints.

The Android app generates a random device key on first launch, keeps it in encrypted storage and
calls ``POST /auth/anonymous``. The server maps the key to an ordinary ``User`` row (email derived
from a SHA-256 of the key, password hash of the key), so existing per-user case storage, case chat,
Charge Check and ``POST /me/delete`` (password = device key) keep working unchanged.

Rate limits are in-memory per process (the API runs one uvicorn worker on Railway). They reset on
redeploy, which is acceptable for cost protection; they are not a security boundary for data.
"""
from __future__ import annotations

import hashlib
import os
import re
import threading
import time
from collections import defaultdict

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models
from .auth import ALGORITHM, AUDIENCE, ISSUER, SECRET, create_token, hash_password, verify_password
from .database import get_db
from .token_service import issue_refresh

ANON_EMAIL_DOMAIN = "anonymous.galaw.invalid"
DAY = 86400

AI_DEVICE_DAILY_LIMIT = int(os.getenv("AI_DEVICE_DAILY_LIMIT", "40"))
AI_IP_DAILY_LIMIT = int(os.getenv("AI_IP_DAILY_LIMIT", "150"))
ANON_CREATE_IP_DAILY_LIMIT = int(os.getenv("ANON_CREATE_IP_DAILY_LIMIT", "10"))

AI_LIMIT_MESSAGE = (
    "You've reached today's limit for AI answers on GA.LAW.HELP. This keeps the app free for everyone. "
    "Please try again tomorrow. Laws search, Funny Laws and your saved cases still work. "
    "If you are in danger, call 911."
)
ANON_LIMIT_MESSAGE = "Too many new devices from this network today. Please try again tomorrow."

# POST paths that call the AI provider.
_AI_PATHS = (
    re.compile(r"^/public/rights-assistant/?$"),
    re.compile(r"^/public/ask/?$"),
    re.compile(r"^/charge-check/?$"),
    re.compile(r"^/civil-check/?$"),
    re.compile(r"^/loopholes/analyze/?$"),
    re.compile(r"^/internal/legal-assistant/?$"),
    re.compile(r"^/cases/\d+/(chat|charge-check|civil-check|motion-screen|innocence-analysis|defense-analysis|analysis/run)/?$"),
)


def is_ai_path(method: str, path: str) -> bool:
    return method.upper() == "POST" and any(p.match(path) for p in _AI_PATHS)


class DailyCounter:
    """Fixed 24-hour windows per key. Thread-safe, in-memory."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))

    def hit(self, key: str, limit: int, now: float | None = None) -> bool:
        """Count one hit; return False (and do not count) if the key is already at ``limit``."""
        now = time.time() if now is None else now
        with self._lock:
            start, count = self._hits[key]
            if now - start >= DAY:
                start, count = now, 0
            if count >= limit:
                self._hits[key] = (start, count)
                return False
            self._hits[key] = (start, count + 1)
            if len(self._hits) > 200_000:  # bound memory
                cutoff = now - DAY
                for k in [k for k, (s, _) in self._hits.items() if s < cutoff]:
                    del self._hits[k]
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


ai_counter = DailyCounter()
anon_create_counter = DailyCounter()


def client_ip(request: Request) -> str:
    real = request.headers.get("x-real-ip", "").strip()
    if real:
        return real
    forwarded = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    if forwarded:
        return forwarded[-1]  # hop appended by the platform proxy
    return request.client.host if request.client else "unknown"


def _token_subject(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("bearer "):
        return None
    try:
        payload = jwt.decode(header[7:].strip(), SECRET, algorithms=[ALGORITHM], audience=AUDIENCE, issuer=ISSUER)
        return str(payload["sub"])
    except Exception:
        return None


async def ai_rate_limit_middleware(request: Request, call_next):
    if is_ai_path(request.method, request.url.path):
        subject = _token_subject(request)
        if subject is not None and not ai_counter.hit("user:" + subject, AI_DEVICE_DAILY_LIMIT):
            return JSONResponse({"detail": AI_LIMIT_MESSAGE, "rate_limited": True}, status_code=429, headers={"Retry-After": "3600"})
        if not ai_counter.hit("ip:" + client_ip(request), AI_IP_DAILY_LIMIT):
            return JSONResponse({"detail": AI_LIMIT_MESSAGE, "rate_limited": True}, status_code=429, headers={"Retry-After": "3600"})
    return await call_next(request)


def anonymous_email(device_key: str) -> str:
    return "device-" + hashlib.sha256(device_key.encode("utf-8")).hexdigest()[:40] + "@" + ANON_EMAIL_DOMAIN


def is_anonymous_email(email: str | None) -> bool:
    return bool(email) and str(email).lower().endswith("@" + ANON_EMAIL_DOMAIN)


class AnonymousAuthRequest(BaseModel):
    # Random secret generated on the device (>= 128 bits). Never logged.
    device_key: str = Field(min_length=32, max_length=256, pattern=r"^[A-Za-z0-9_\-]+$")


router = APIRouter()


@router.post("/auth/anonymous")
def anonymous_session(body: AnonymousAuthRequest, request: Request, db: Session = Depends(get_db)):
    """Return a session for this device, creating its anonymous identity on first use."""
    email = anonymous_email(body.device_key)
    user = db.query(models.User).filter_by(email=email).first()
    created = False
    if user is None:
        if not anon_create_counter.hit("ip:" + client_ip(request), ANON_CREATE_IP_DAILY_LIMIT):
            raise HTTPException(429, ANON_LIMIT_MESSAGE)
        user = models.User(email=email, password_hash=hash_password(body.device_key), role="user")
        db.add(user)
        db.flush()
        db.add(models.AuditLog(user_id=user.id, action="ANONYMOUS_DEVICE_CREATED", object_type="user", object_id=user.id))
        created = True
    elif not verify_password(body.device_key, user.password_hash) or not user.is_active:
        raise HTTPException(401, "Device identity is unavailable")
    refresh = issue_refresh(db, user.id)
    db.commit()
    return {
        "access_token": create_token(user.id),
        "refresh_token": refresh,
        "token_type": "bearer",
        "anonymous": True,
        "created": created,
        "user": {"id": user.id},
    }
