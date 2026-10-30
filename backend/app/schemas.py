from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=15, max_length=128)
class Login(BaseModel):
    email: EmailStr
    password: str
class CaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    case_number: str | None = None
    county: str | None = None
    case_type: str = 'criminal'
    stage: str | None = None
    narrative: str | None = Field(default=None, max_length=100_000)

class CaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    case_number: str | None = Field(default=None, max_length=100)
    county: str | None = Field(default=None, max_length=100)
    case_type: str | None = Field(default=None, max_length=40)
    stage: str | None = Field(default=None, max_length=80)
    narrative: str | None = Field(default=None, max_length=100_000)
class TimelineCreate(BaseModel):
    occurred_at: datetime | None = None
    event_type: str
    title: str
    details: str | None = None
    source_label: str = 'USER_REPORTED'
    source_ref: str | None = None

class UploadInit(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    media_type: str = Field(default='application/octet-stream', max_length=100)
    total_chunks: int = Field(ge=1, le=100_000)
    total_bytes: int | None = Field(default=None, ge=1)


class AuthorityCreate(BaseModel):
    jurisdiction: str = "Georgia"
    authority_type: str
    citation: str
    title: str | None = None
    text: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    status: str = "UNVERIFIED"
    source_url: str | None = None

class AuthorityVersionCreate(BaseModel):
    version_label: str | None = None
    text: str
    effective_from: date | None = None
    effective_to: date | None = None
    source_url: str
    verification_status: str = "UNVERIFIED"

class AuthorityLinkCreate(BaseModel):
    authority_id: int
    authority_version_id: int | None = None
    proposition: str
    pinpoint: str | None = None
    source_location: str | None = None
    relevance: str = "SUPPORTING"
    verified: bool = False

class CaseAnalysisRequest(BaseModel):
    focus: str = "full_case"
    event_date: date | None = None

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=15, max_length=128)

class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class CaseNoteCreate(BaseModel):
    title: str = Field(default="Saved legal research", min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=100_000)
    note_type: str = Field(default="LEGAL_RESEARCH", max_length=40)
    language: str = Field(default="en", max_length=12)

class AccountDeleteRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)
    confirm: str = Field(min_length=1, max_length=20)
