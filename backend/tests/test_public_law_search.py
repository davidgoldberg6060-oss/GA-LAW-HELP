from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import LegalAuthority
from app.authority_search_service import public_law_search


def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    rows = [
        ("statute", "O.C.G.A. § 16-11-131", "Possession of firearms by convicted felons", "OFFICIAL"),
        ("statute", "O.C.G.A. § 16-11-126", "Carrying a weapon without a license", "OFFICIAL"),
        ("statute", "O.C.G.A. § 17-6-12", "Release on own recognizance", "OFFICIAL"),
        ("regulation", "Ga. Comp. R. & Regs. 570-1-1", "Weapons carry license rules", "OFFICIAL"),
        ("case_law", "S26A0001", "Lowe v. State weapon search", "VERIFIED"),
        ("case_law", "S26A0002", "Sealed weapon matter", "SEALED"),
        ("court_rule", "Ct. App. R. 1", "Weapon exhibits in court", "OFFICIAL"),
    ]
    for kind, citation, text, status in rows:
        db.add(LegalAuthority(jurisdiction="Georgia", authority_type=kind, citation=citation, title=f"{citation}. {text}",
                              text=text, status=status, source_url="https://example.gov/x", retrieved_at=datetime.utcnow(),
                              currency_status="current", precedential_status="unknown"))
    db.commit()
    return db


def test_tabs_filter_by_authority_type_and_exclude_restricted_records():
    db = session()
    statutes = {r.citation for r in public_law_search(db, kind="statutes", keyword="weapon")}
    assert "O.C.G.A. § 16-11-126" in statutes and "Ga. Comp. R. & Regs. 570-1-1" in statutes
    assert all(not c.startswith("S26") for c in statutes)
    assert "Ct. App. R. 1" in statutes  # Laws tab includes court rules (labelled by type)
    cases = [r.citation for r in public_law_search(db, kind="case_law", keyword="weapon")]
    assert cases == ["S26A0001"]
    rules = [r.citation for r in public_law_search(db, kind="court_rules", keyword="weapon")]
    assert rules == ["Ct. App. R. 1"]


def test_title_and_chapter_browse_statutes_by_citation_prefix():
    db = session()
    title16 = [r.citation for r in public_law_search(db, kind="statutes", title="16")]
    assert title16 == ["O.C.G.A. § 16-11-126", "O.C.G.A. § 16-11-131"]
    assert [r.citation for r in public_law_search(db, kind="statutes", title="17", chapter="6")] == ["O.C.G.A. § 17-6-12"]
    assert public_law_search(db, kind="statutes") == []
    with pytest.raises(ValueError):
        public_law_search(db, kind="statutes", title="16%")
    with pytest.raises(ValueError):
        public_law_search(db, kind="secret", keyword="x")


def test_public_law_route_is_guest_and_never_reads_private_tables():
    source = Path("app/main.py").read_text(encoding="utf-8")
    route = source.split("@app.get('/public/georgia-laws/search')", 1)[1].split("def _guest_rights_without_corpus", 1)[0]
    assert "public_law_search(" in route
    assert "Depends(current_user)" not in route and "Depends(require_paid)" not in route
    assert "models.Case" not in route and "owned_case(" not in route
