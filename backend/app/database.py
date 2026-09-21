import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ga_law_help.db")
EXPECTED_TABLES = {
    "users", "cases", "timeline_events", "evidence", "evidence_findings",
    "upload_sessions", "analysis_jobs", "legal_sources", "legal_authorities",
    "authority_versions", "case_authority_links", "issue_analyses",
    "audit_logs", "refresh_tokens", "password_reset_tokens",
    "email_verification_tokens", "case_notes",
}

def engine_options(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}, "pool_pre_ping": True}
    connect_args = {}
    transaction_pooler = os.getenv("DATABASE_POOL_MODE", "").lower() == "transaction" or ":6543/" in url
    if transaction_pooler:
        # Supabase transaction pooling does not support prepared statements.
        connect_args["prepare_threshold"] = None
    return {
        "connect_args": connect_args,
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "5")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE_SECONDS", "300")),
    }

engine = create_engine(DATABASE_URL, **engine_options(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def database_health() -> dict:
    with engine.connect() as connection:
        connection.execute(text("select 1"))
    return {"database": "ok"}

def verify_production_schema() -> None:
    database_health()
    existing = set(inspect(engine).get_table_names())
    missing = sorted(EXPECTED_TABLES - existing)
    if missing:
        raise RuntimeError(
            "Database migrations are incomplete; missing tables: " + ", ".join(missing)
        )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
