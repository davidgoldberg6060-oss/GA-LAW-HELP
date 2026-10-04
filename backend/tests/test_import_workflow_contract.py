"""The opinion import workflow is manual, previews by default, and commits only with a real secret."""
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/import-supreme-opinions.yml"


def test_import_workflow_is_manual_preview_by_default_and_guards_commit():
    text = WORKFLOW.read_text(encoding="utf-8")
    on_block = text.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
    assert "workflow_dispatch:" in on_block
    for trigger in ("push:", "pull_request:", "schedule:"):
        assert trigger not in on_block
    commit_input = text.split("      commit:\n", 1)[1].split("\npermissions:", 1)[0]
    assert "default: false" in commit_input and "type: boolean" in commit_input
    preview = text.split("- name: Preview import (no database writes)", 1)[1].split("- name:", 1)[0]
    assert "if: ${{ !inputs.commit }}" in preview
    assert "--commit" not in preview and "DATABASE_URL" not in preview
    commit = text.split("- name: Commit import to DATABASE_URL", 1)[1]
    assert "if: ${{ inputs.commit }}" in commit
    assert "DATABASE_URL: ${{ secrets.DATABASE_URL }}" in commit
    assert 'if [ -z "$DATABASE_URL" ]' in commit
    # inputs reach the shell only through env vars (no ${{ inputs.* }} inside run scripts)
    for block in (preview, commit):
        run = block.split("run:", 1)[1]
        assert "${{" not in run
    assert "permissions:\n  contents: read" in text
