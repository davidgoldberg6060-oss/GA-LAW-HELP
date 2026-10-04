from datetime import UTC, datetime, date
from sqlalchemy import String, Text, DateTime, Date, ForeignKey, Integer, BigInteger, Boolean, CheckConstraint, Index, text as sql_text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
from .legal_status_vocabulary import CURRENCY_STATUSES, PRECEDENTIAL_STATUSES, sql_in_list

def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    case_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    case_type: Mapped[str] = mapped_column(String(40), default="criminal")
    stage: Mapped[str | None] = mapped_column(String(80), nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    events = relationship("TimelineEvent", cascade="all, delete-orphan")
    evidence = relationship("Evidence", cascade="all, delete-orphan")

class CaseNote(Base):
    __tablename__ = "case_notes"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    note_type: Mapped[str] = mapped_column(String(40), default="LEGAL_RESEARCH")
    title: Mapped[str] = mapped_column(String(255), default="Saved legal research")
    content: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(12), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    event_type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(255))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_label: Mapped[str] = mapped_column(String(40), default="USER_REPORTED")
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(100))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    storage_key: Mapped[str] = mapped_column(String(500))
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    original_preserved: Mapped[bool] = mapped_column(Boolean, default=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    findings = relationship("EvidenceFinding", cascade="all, delete-orphan")

class EvidenceFinding(Base):
    __tablename__ = "evidence_findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id"), index=True)
    start_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    finding_type: Mapped[str] = mapped_column(String(60))
    evidence_label: Mapped[str] = mapped_column(String(30))
    text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)

class LegalAuthority(Base):
    __tablename__ = "legal_authorities"
    __table_args__ = (
        CheckConstraint(f"lower(currency_status) IN ({sql_in_list(CURRENCY_STATUSES)})", name="ck_legal_authorities_currency_status"),
        CheckConstraint(f"lower(precedential_status) IN ({sql_in_list(PRECEDENTIAL_STATUSES)})", name="ck_legal_authorities_precedential_status"),
        # Full-text search (Postgres only); keep in sync with authority_search_service and
        # backend/migrations/20261004_authority_fulltext_search.sql.
        Index(
            "ix_legal_authorities_fulltext",
            sql_text("to_tsvector('english'::regconfig, ((COALESCE(citation, '') || ' ') || COALESCE(title, '') || ' ') || COALESCE(text, ''))"),
            postgresql_using="gin",
        ).ddl_if(dialect="postgresql"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    jurisdiction: Mapped[str] = mapped_column(String(100), index=True)
    authority_type: Mapped[str] = mapped_column(String(50))
    citation: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="UNVERIFIED")
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    currency_status: Mapped[str] = mapped_column(String(40), default="unknown")
    precedential_status: Mapped[str] = mapped_column(String(40), default="unknown")
    status_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status_source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    superseding_authority: Mapped[str | None] = mapped_column(String(500), nullable=True)
    negative_treatment: Mapped[str | None] = mapped_column(Text, nullable=True)

class IssueAnalysis(Base):
    __tablename__ = "issue_analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    issue: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(80))
    favors: Mapped[str] = mapped_column(String(30))
    analysis: Mapped[str] = mapped_column(Text)
    counterargument: Mapped[str | None] = mapped_column(Text, nullable=True)
    facts_needed: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), default="NEEDS_REVIEW")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100))
    object_type: Mapped[str] = mapped_column(String(60))
    object_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class UploadSession(Base):
    __tablename__ = "upload_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    total_chunks: Mapped[int] = mapped_column(Integer)
    total_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="UPLOADING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id"), index=True)
    job_type: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(30), default="QUEUED", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class LegalSource(Base):
    __tablename__ = "legal_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="Georgia")
    base_url: Mapped[str] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(60))
    official: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

class AuthorityVersion(Base):
    __tablename__ = "authority_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    authority_id: Mapped[int] = mapped_column(ForeignKey("legal_authorities.id"), index=True)
    version_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    source_url: Mapped[str] = mapped_column(String(1000))
    content_sha256: Mapped[str] = mapped_column(String(64), index=True)
    verification_status: Mapped[str] = mapped_column(String(40), default="UNVERIFIED")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class CaseAuthorityLink(Base):
    __tablename__ = "case_authority_links"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    authority_id: Mapped[int] = mapped_column(ForeignKey("legal_authorities.id"), index=True)
    authority_version_id: Mapped[int | None] = mapped_column(ForeignKey("authority_versions.id"), nullable=True)
    proposition: Mapped[str] = mapped_column(Text)
    pinpoint: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    relevance: Mapped[str] = mapped_column(String(30), default="SUPPORTING")
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    replaced_by_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class EmailVerificationToken(Base):
    __tablename__ = 'email_verification_tokens'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
