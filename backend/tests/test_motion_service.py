from app.motion_service import build_motion_registry, verified_motion_context


class Authority:
    def __init__(self, ident, text, status="CURRENT", source="https://official.example/opinion"):
        self.id = ident
        self.citation = f"Citation {ident}"
        self.text = text
        self.status = status
        self.source_url = source


class Version:
    def __init__(self, status="VERIFIED", source="https://official.example/version"):
        self.verification_status = status
        self.source_url = source


def test_discovered_motion_becomes_verified_only_with_verified_version():
    authority = Authority(1, "The motion to suppress evidence was denied.", status="UNVERIFIED")
    unverified = build_motion_registry([authority], {})
    row = next(x for x in unverified["motions"] if x["name"] == "Motion to Suppress Evidence")
    assert row["verification_status"] == "NEEDS_VERIFICATION"

    verified = build_motion_registry([authority], {1: [Version()]})
    row = next(x for x in verified["motions"] if x["name"] == "Motion to Suppress Evidence")
    assert row["verification_status"] == "VERIFIED_CURRENT"
    assert row["verified_authorities"]


def test_ai_context_excludes_unverified_candidates():
    registry = build_motion_registry([
        Authority(1, "The motion to suppress evidence was denied.", status="UNVERIFIED"),
        Authority(2, "A motion for new trial was filed.", status="UNVERIFIED"),
    ], {1: [Version()]})
    context = verified_motion_context(registry)
    assert "Motion to Suppress Evidence" in context
    assert "Motion for New Trial" not in context


def test_coverage_counts_identified_registry():
    registry = build_motion_registry([], {})
    assert registry["coverage"]["identified"] >= 10
    assert registry["coverage"]["UNRECOGNIZED_RESEARCH_REQUIRED"] >= 10
