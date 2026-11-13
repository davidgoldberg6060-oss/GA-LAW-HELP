"""Android renders server help_resources as tappable https/tel buttons; loved-one button only from the user's words."""
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "android/app/src/main/java/help/galaw/standalone"
HOME = (SRC / "HomeActivity.kt").read_text()
CTRL = (SRC / "TalkToMeController.kt").read_text()
LOVED = (SRC / "HelpLovedOne.kt").read_text()


def test_help_resources_parsed_https_only_and_tel_digits():
    assert 'optJSONArray("help_resources")' in CTRL and 'url.startsWith("https://")' in CTRL
    assert '"tel:$digits"' in CTRL


def test_buttons_rendered_with_accessible_labels():
    assert "reply.helpResources.forEach" in HOME and 'contentDescription="Call "' in HOME


def test_loved_one_button_uses_question_only_and_not_child_visitation():
    assert "HelpLovedOne.CUSTODY.containsMatchIn(q)" in HOME
    assert 'containsMatchIn(q+" "+text)' not in HOME
    assert "|visitation|" not in LOVED
