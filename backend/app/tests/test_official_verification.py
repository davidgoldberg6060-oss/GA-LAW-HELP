"""Official-source verification side table: verified rows become citable support with an as-of date."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.database import Base
from app.models import AuthorityVerification, LegalAuthority, VerificationSource
from app.authority_search_service import (AMENDMENT_NOTE, exact_citation_results, persisted_authority_hits,
                                          with_as_of)
from app.charge_check_service import lookup_sections
from app.grounded_legal_assistant import grounded_legal_response

URL = "https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.44.odt#44-7-34"


def _db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(LegalAuthority(id=1, jurisdiction="Georgia", authority_type="statute", citation="O.C.G.A. § 44-7-34",
                          title="Return of security deposit", status="UNVERIFIED", source_url=URL,
                          text="Within one month after termination of the residential lease the landlord shall return the security deposit."))
    db.add(LegalAuthority(id=2, jurisdiction="Georgia", authority_type="statute", citation="O.C.G.A. § 44-7-35",
                          title="Security deposit damages list", status="UNVERIFIED", source_url=URL,
                          text="Security deposit statement of damages."))
    db.add(VerificationSource(id=1, source_key="pro", source_name="O.C.G.A. (Public.Resource.Org)",
                              source_url="https://archive.org/details/gov.ga.ocga.2018",
                              as_of_label="text as of 2022 edition", method="official_source_provenance"))
    db.add(AuthorityVerification(authority_id=1, source_id=1))
    db.commit()
    return db


def test_with_as_of():
    assert with_as_of("O.C.G.A. § 44-7-34", "text as of 2022 edition") == "O.C.G.A. § 44-7-34 (text as of 2022 edition)"
    assert with_as_of("O.C.G.A. § 44-7-34", None) == "O.C.G.A. § 44-7-34"


def test_only_side_table_rows_become_usable():
    db = _db()
    rows = {r.citation: r for r in exact_citation_results(db, ["O.C.G.A. § 44-7-34", "O.C.G.A. § 44-7-35"])}
    assert rows["O.C.G.A. § 44-7-34"].usable_as_support and rows["O.C.G.A. § 44-7-34"].status == "verified"
    assert rows["O.C.G.A. § 44-7-34"].display_citation.endswith("(text as of 2022 edition)")
    assert not rows["O.C.G.A. § 44-7-35"].usable_as_support
    hits = persisted_authority_hits(db, "security deposit", limit=5)
    assert any(h["usable_as_support"] and h["as_of"] for h in hits)


def test_lookup_sections_overlay():
    hits = {h["citation"]: h for h in lookup_sections(_db(), ["44-7-34", "44-7-35"])}
    assert hits["O.C.G.A. § 44-7-34"]["verification_status"] == "verified"
    assert hits["O.C.G.A. § 44-7-35"]["verification_status"] == "unverified"


def test_grounded_answer_cites_with_as_of_and_note():
    prompts = []
    def ask(prompt):
        prompts.append(prompt)
        return "SHORT ANSWER\nAsk for it back.\nIMPORTANT LIMITATIONS\nNot legal advice."
    out = grounded_legal_response("my landlord won't return my security deposit", "general", ask, db=_db())
    assert out["grounded_authority_count"] >= 1
    assert "Text as of: text as of 2022 edition" in prompts[0]
    assert AMENDMENT_NOTE in out["analysis"]
    cited = [a for a in out["authorities"] if a.get("as_of")]
    assert cited and all("(text as of 2022 edition)" in a["citation"] for a in cited)
