"""Guest rights stay public. Private case routes stay authenticated."""
from pathlib import Path


def test_public_rights_routes_do_not_require_login():
    main = Path("app/main.py").read_text(encoding="utf-8")
    rights = Path("app/public_rights.py").read_text(encoding="utf-8")
    assistant = main.split("@app.post('/public/rights-assistant')", 1)[1].split(
        "@app.post('/cases/{case_id}/motion-screen')", 1
    )[0]
    assert "def public_rights_assistant" in assistant
    assert "Depends(require_paid)" not in assistant
    assert "Depends(current_user)" not in assistant
    assert "login_required'] = False" in assistant or "'login_required': False" in assistant
    assert "_guest_rights_without_corpus" in assistant
    assert "not a claim that any rule is current Georgia law" in main
    assert "Do not resist, lie, or destroy evidence" in main
    assert '@router.get("/encounter")' in rights
    assert "require_paid" not in rights
    assert "current_user" not in rights


def test_private_motion_screen_stays_login_only():
    main = Path("app/main.py").read_text(encoding="utf-8")
    screen = main.split("@app.post('/cases/{case_id}/motion-screen')", 1)[1].split(
        "@app.post('/cases/{case_id}/innocence-analysis')", 1
    )[0]
    assert "Depends(require_paid)" in screen
    assert "owned_case(" in screen
