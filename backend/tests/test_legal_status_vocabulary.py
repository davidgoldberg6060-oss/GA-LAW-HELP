"""One consistent status vocabulary across ingestion, persistence, the model and the migration."""
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ingestion import adapters, coverage, persistence
from app.ingestion.models import LegalStatus
from app.ingestion.persistence import _merge_status
from app.legal_status_vocabulary import (
    CURRENCY_STATUSES,
    NEGATIVE_TREATMENTS,
    PRECEDENTIAL_STATUSES,
    normalize_currency_status,
    normalize_precedential_status,
)
from app.models import LegalAuthority

MIGRATION = Path(__file__).resolve().parents[1] / "migrations/20261004_authority_status_vocabulary.sql"


def _sql_set(sql: str, constraint: str) -> set[str]:
    block = sql.split(f"ADD CONSTRAINT {constraint}", 1)[1].split(";", 1)[0]
    return set(re.findall(r"'([a-z_]+)'", block))


def test_every_value_the_ingestion_code_writes_is_in_the_vocabulary():
    # adapters store the detected treatment (or "current"/"unknown") as currency_status
    assert set(adapters._NEGATIVE_PATTERNS) <= CURRENCY_STATUSES
    assert {"current", "unknown"} <= CURRENCY_STATUSES
    assert persistence._NEGATIVE == NEGATIVE_TREATMENTS
    assert coverage._NEGATIVE == NEGATIVE_TREATMENTS
    assert NEGATIVE_TREATMENTS <= PRECEDENTIAL_STATUSES
    # "binding" is the positive precedential value used by the code/tests; "nonprecedential"
    # is the value motion_service treats as negative.
    assert {"binding", "nonprecedential", "unknown"} <= PRECEDENTIAL_STATUSES
    assert "negative_treatment" not in CURRENCY_STATUSES
    assert "precedential" not in PRECEDENTIAL_STATUSES


def test_migration_constraints_match_the_python_vocabulary():
    sql = MIGRATION.read_text(encoding="utf-8")
    assert _sql_set(sql, "ck_legal_authorities_currency_status") == set(CURRENCY_STATUSES)
    assert _sql_set(sql, "ck_legal_authorities_precedential_status") == set(PRECEDENTIAL_STATUSES)
    assert "NOT VALID" in sql and "VALIDATE CONSTRAINT" in sql
    for line in sql.splitlines():
        if line.startswith("UPDATE"):
            assert "lower(btrim(" in line or "= 'unknown' WHERE" in line, line


def test_normalizers_are_conservative():
    assert normalize_currency_status(" CURRENT ") == "current"
    assert normalize_currency_status(None) == "unknown"
    assert normalize_currency_status("probably fine") == "unknown"
    assert normalize_precedential_status("Binding") == "binding"
    assert normalize_precedential_status("precedential") == "unknown"


def test_merge_status_normalizes_case_and_never_writes_unrecognized_values():
    class Stub:
        status = "OFFICIAL"
        currency_status = "unknown"
        precedential_status = "binding"
        status_checked_at = None
        status_source_url = None
        superseding_authority = None
        negative_treatment = None

    authority = Stub()
    _merge_status(authority, LegalStatus(verification_status="official", currency_status="CURRENT", precedential_status="made-up"))
    assert authority.currency_status == "current"
    assert authority.precedential_status == "binding"


@pytest.fixture()
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as db:
        yield db


def _authority(**overrides) -> LegalAuthority:
    values = dict(jurisdiction="Georgia", authority_type="case", citation="Test v. State", status="OFFICIAL",
                  source_url="https://www.gasupreme.us/x", retrieved_at=datetime.now(timezone.utc).replace(tzinfo=None))
    values.update(overrides)
    return LegalAuthority(**values)


@pytest.mark.parametrize("currency", sorted(CURRENCY_STATUSES))
def test_database_accepts_every_vocabulary_currency_value(session, currency):
    session.add(_authority(currency_status=currency, precedential_status="binding"))
    session.commit()


@pytest.mark.parametrize("column,value", [("currency_status", "negative_treatment"), ("precedential_status", "precedential"), ("currency_status", "valid")])
def test_database_rejects_values_outside_the_vocabulary(session, column, value):
    session.add(_authority(**{column: value}))
    with pytest.raises(IntegrityError):
        session.commit()
