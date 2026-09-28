from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANDROID = ROOT / "android/app/src/main/java/help/galaw/standalone/InternalLegalSearchActivity.kt"
BACKEND = ROOT / "backend/app/grounded_legal_assistant.py"

FIELDS = (
    "what_appears_to_be_happening",
    "safest_immediate_steps",
    "your_rights",
    "law_enforcement_may_may_not_do",
    "what_to_say_or_do",
    "verified_georgia_authority",
    "important_limitations",
)


def test_android_consumes_typed_talk_to_me_sections():
    source = ANDROID.read_text(encoding="utf-8")
    assert 'response.optJSONObject("sections")' in source
    for field in FIELDS:
        assert f'"{field}"' in source


def test_backend_and_android_share_talk_to_me_section_names():
    android = ANDROID.read_text(encoding="utf-8")
    backend = BACKEND.read_text(encoding="utf-8")
    for field in FIELDS:
        assert f'"{field}"' in android
        assert field in backend


def test_android_keeps_verified_authorities_separate_from_guidance_cards():
    source = ANDROID.read_text(encoding="utf-8")
    assert 'Verified Supporting Authorities' in source
    assert 'renderAuthorities(root,response.optJSONArray("authorities"),true)' in source
