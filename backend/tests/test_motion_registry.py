from app.motion_registry import classify_verification, coverage_summary, normalize_motion_name, seed_catalog


def test_seed_catalog_is_explicitly_nonempty():
    rows = seed_catalog()
    assert len(rows) >= 10
    assert any(row["name"] == "Motion to Suppress Evidence" for row in rows)
    assert any(row["name"] == "Motion for New Trial" for row in rows)


def test_normalize_motion_name():
    assert normalize_motion_name("  Motion-to-Suppress   Evidence ") == "motion to suppress evidence"


def test_verification_requires_official_source_and_verified_status():
    assert classify_verification(["CURRENT"], True) == "VERIFIED_CURRENT"
    assert classify_verification(["CURRENT"], False) == "NEEDS_VERIFICATION"
    assert classify_verification(["SUPERSEDED"], True) == "VERIFIED_HISTORICAL"
    assert classify_verification([], False) == "UNRECOGNIZED_RESEARCH_REQUIRED"


def test_coverage_summary_is_auditable():
    summary = coverage_summary([
        {"verification_status": "VERIFIED_CURRENT"},
        {"verification_status": "VERIFIED_CURRENT"},
        {"verification_status": "NEEDS_VERIFICATION"},
    ])
    assert summary["identified"] == 3
    assert summary["VERIFIED_CURRENT"] == 2
    assert summary["NEEDS_VERIFICATION"] == 1
