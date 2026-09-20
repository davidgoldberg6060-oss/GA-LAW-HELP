from app.database import EXPECTED_TABLES, engine_options


def test_transaction_pooler_disables_prepared_statements(monkeypatch):
    monkeypatch.setenv("DATABASE_POOL_MODE", "transaction")
    options = engine_options("postgresql+psycopg://user:pass@pooler.example:6543/postgres")
    assert options["connect_args"]["prepare_threshold"] is None
    assert options["pool_pre_ping"] is True


def test_sqlite_config_keeps_thread_override(monkeypatch):
    monkeypatch.delenv("DATABASE_POOL_MODE", raising=False)
    options = engine_options("sqlite:///test.db")
    assert options["connect_args"]["check_same_thread"] is False


def test_production_schema_contract_includes_security_tables():
    assert {"users", "refresh_tokens", "password_reset_tokens", "email_verification_tokens"} <= EXPECTED_TABLES
