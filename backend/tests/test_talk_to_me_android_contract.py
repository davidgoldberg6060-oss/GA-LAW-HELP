from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANDROID = ROOT / "android/app/src/main/java/help/galaw/standalone/InternalLegalSearchActivity.kt"
BACKEND = ROOT / "backend/app/grounded_legal_assistant.py"

MODE_FIELDS = {
    "talk_to_me": (
        "what_appears_to_be_happening", "safest_immediate_steps", "your_rights",
        "law_enforcement_limits", "lawful_things_to_say_or_do",
    ),
    "case_analysis": (
        "facts_to_verify", "legal_issues", "prosecution_arguments", "defense_arguments",
        "possible_motions", "practical_next_steps",
    ),
    "rights": (
        "situation", "rights_that_may_apply", "law_enforcement_authority",
        "law_enforcement_limits", "lawful_options",
    ),
    "motions": (
        "case_issue", "potential_motions", "required_facts_or_evidence",
        "opposing_arguments", "procedural_questions_to_verify",
    ),
}


def test_android_consumes_typed_grounded_sections():
    source = ANDROID.read_text(encoding="utf-8")
    assert 'response.optJSONObject("sections")' in source
    for mode, fields in MODE_FIELDS.items():
        assert f'"{mode}"' in source
        for field in fields:
            assert f'"{field}"' in source


def test_backend_and_android_share_all_grounded_section_names():
    android = ANDROID.read_text(encoding="utf-8")
    backend = BACKEND.read_text(encoding="utf-8")
    for fields in MODE_FIELDS.values():
        for field in fields:
            assert f'"{field}"' in android
            assert f'"{field}"' in backend


def test_android_keeps_verified_authorities_separate_from_guidance_cards():
    source = ANDROID.read_text(encoding="utf-8")
    assert 'Laws cited' in source
    assert 'GroundedLegalResult.lawsCited(response)' in source


def test_native_renderers_exist_for_every_grounded_mode():
    source = ANDROID.read_text(encoding="utf-8")
    for renderer in (
        "renderTypedTalkToMe", "renderTypedCaseAnalysis", "renderTypedRights", "renderTypedMotions"
    ):
        assert renderer in source


def test_backend_preserves_no_fabricated_authority_guardrails():
    source = BACKEND.read_text(encoding="utf-8")
    assert "never create a citation, case, statute, rule, deadline, sentence, or procedural requirement" in source
    assert "MUST NOT present a Georgia-specific proposition as verified" in source
    assert "do not fill it from memory" in source
