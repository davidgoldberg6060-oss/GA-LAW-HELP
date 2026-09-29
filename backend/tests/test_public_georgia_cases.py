from pathlib import Path
from types import SimpleNamespace

from app.public_case_service import (
    is_public_georgia_case,
    public_case_payload,
    safe_public_source_url,
)


def _authority(**changes):
    values = {
        "id": 7,
        "title": "Example v. State",
        "citation": "123 Ga. 456",
        "authority_type": "Georgia appellate case opinion",
        "jurisdiction": "Georgia",
        "status": "VERIFIED",
        "source_url": "https://www.gasupreme.us/example",
        "effective_from": None,
        "effective_to": None,
        "retrieved_at": None,
        "text": "Published opinion text.",
    }
    values.update(changes)
    return SimpleNamespace(**values)


def test_public_case_policy_accepts_public_georgia_opinions():
    assert is_public_georgia_case(_authority())


def test_public_case_policy_excludes_nonpublic_and_noncase_records():
    for status in ("SEALED", "JUVENILE", "EXPUNGED", "RESTRICTED", "PRIVATE", "UNAVAILABLE"):
        assert not is_public_georgia_case(_authority(status=status))
    assert not is_public_georgia_case(_authority(jurisdiction="Florida"))
    assert not is_public_georgia_case(_authority(authority_type="Georgia statute"))


def test_public_case_payload_never_emits_unsafe_source_urls():
    assert safe_public_source_url("http://example.com") is None
    assert safe_public_source_url("javascript:alert(1)") is None
    assert public_case_payload(_authority())["source_url"].startswith("https://")


def test_public_case_routes_do_not_require_ownership_or_read_private_case_tables():
    source = Path("app/main.py").read_text(encoding="utf-8")
    list_route = source.split("@app.get('/public/georgia-cases')", 1)[1].split(
        "@app.get('/public/georgia-cases/{authority_id}')", 1
    )[0]
    detail_route = source.split("@app.get('/public/georgia-cases/{authority_id}')", 1)[1].split(
        "@app.post('/cases/{case_id}/", 1
    )[0]
    routes = list_route + detail_route

    assert "models.LegalAuthority" in routes
    assert "Depends(current_user)" not in routes
    assert "Depends(require_paid)" not in routes
    assert "owned_case(" not in routes
    assert "models.Case" not in routes


def test_public_case_service_cannot_import_private_workspace_models():
    source = Path("app/public_case_service.py").read_text(encoding="utf-8")
    for private_model in ("Case", "Evidence", "CaseNote", "TimelineEvent", "UploadSession"):
        assert f"models.{private_model}" not in source
