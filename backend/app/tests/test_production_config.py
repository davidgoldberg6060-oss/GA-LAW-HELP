import pytest

from app.main import validate_production_config
from app.worker import validate_worker_config


def configure_valid_production(monkeypatch):
    values = {
        "ENVIRONMENT": "production",
        "JWT_SECRET": "a-production-secret-with-at-least-32-characters",
        "DATABASE_URL": "postgresql+psycopg://user:pass@db.example/postgres?sslmode=require",
        "DEV_EXPOSE_RESET_TOKEN": "false",
        "DEV_EXPOSE_VERIFICATION_TOKEN": "false",
        "STORAGE_BACKEND": "s3",
        "S3_BUCKET": "ga-law-help-evidence",
        "S3_ENDPOINT_URL": "https://project.storage.supabase.co/storage/v1/s3",
        "AWS_REGION": "us-west-2",
        "AWS_ACCESS_KEY_ID": "test-access",
        "AWS_SECRET_ACCESS_KEY": "test-secret",
        "ALLOWED_HOSTS": "api.example.com",
        "REQUIRE_VERIFIED_EMAIL": "true",
        "PUBLIC_APP_URL": "https://app.example.com",
        "MAIL_DELIVERY_MODE": "smtp",
        "SMTP_HOST": "smtp.example.com",
        "SMTP_FROM": "accounts@example.com",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)


def test_valid_production_configuration(monkeypatch):
    configure_valid_production(monkeypatch)
    validate_production_config()


def test_production_database_requires_explicit_ssl(monkeypatch):
    configure_valid_production(monkeypatch)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db.example/postgres")
    with pytest.raises(RuntimeError, match="sslmode"):
        validate_production_config()


def test_production_rejects_local_evidence_storage(monkeypatch):
    configure_valid_production(monkeypatch)
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    with pytest.raises(RuntimeError, match="STORAGE_BACKEND=s3"):
        validate_production_config()


def test_worker_fails_closed_without_production_database(monkeypatch):
    configure_valid_production(monkeypatch)
    monkeypatch.delenv("DATABASE_URL")
    with pytest.raises(RuntimeError, match="PostgreSQL DATABASE_URL"):
        validate_worker_config()
