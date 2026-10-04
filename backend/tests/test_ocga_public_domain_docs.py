"""Georgia v. Public.Resource.Org (2020): the OCGA incl. annotations is not copyrightable.
Docs must not regress to saying it cannot be copied, and must keep the provenance rules."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_docs_reflect_the_2020_ruling_and_provenance_rules():
    policy = (ROOT / "docs/LEGAL_SOURCES_AND_PROVENANCE.md").read_text(encoding="utf-8")
    assert "Georgia v. Public.Resource.Org" in policy and "590 U.S. 255" in policy
    assert "Annotations are not law" in policy
    assert "A release date is not an effective date" in policy
    corpus = (ROOT / "docs/GA_CORPUS_AND_MOTIONS.md").read_text(encoding="utf-8")
    assert "including the full Official Code of Georgia Annotated" in corpus
    for path in list((ROOT / "docs").glob("*.md")) + [ROOT / "backend/app/encounter_rights.py"]:
        text = path.read_text(encoding="utf-8").lower()
        assert "must not copy the official code" not in text, path
        assert "do not copy the official code" not in text, path
