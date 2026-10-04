"""The multi-source import workflow is manual, previews by default, and commits only with a real secret."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/import-legal-sources.yml"
SCRIPT = ROOT / ".github/scripts/run-legal-import.sh"


def test_workflow_is_manual_preview_by_default_and_guards_commit():
    text = WORKFLOW.read_text(encoding="utf-8")
    on_block = text.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
    assert "workflow_dispatch:" in on_block
    for trigger in ("push:", "pull_request:", "schedule:", "workflow_run:"):
        assert trigger not in on_block
    options = on_block.split("options:", 1)[1].split("scope:", 1)[0]
    assert [line.strip("- ").strip() for line in options.strip().splitlines()] == ["ocga", "courtlistener", "appeals", "regulations", "court_rules"]
    commit_input = on_block.split("      commit:\n", 1)[1]
    assert "default: false" in commit_input and "type: boolean" in commit_input
    preview = text.split("- name: Preview import (no database writes)", 1)[1].split("- name:", 1)[0]
    assert "if: ${{ !inputs.commit }}" in preview
    assert "--commit" not in preview and "DATABASE_URL" not in preview
    commit = text.split("- name: Commit import to DATABASE_URL", 1)[1]
    assert "if: ${{ inputs.commit }}" in commit
    assert "DATABASE_URL: ${{ secrets.DATABASE_URL }}" in commit
    assert 'if [ -z "$DATABASE_URL" ]' in commit and "sqlite*)" in commit
    assert commit.rstrip().endswith("bash ../.github/scripts/run-legal-import.sh --commit")
    for block in (preview, commit):
        assert "${{" not in block.split("run:", 1)[1]  # inputs reach the shell only via env vars
    assert "permissions:\n  contents: read" in text
    assert "secrets." not in text.replace("secrets.DATABASE_URL", "")


def test_runner_script_never_commits_on_its_own():
    script = SCRIPT.read_text(encoding="utf-8")
    assert "--commit" not in script.replace("passes --commit only", "")
    assert 'python "${args[@]}" "$@"' in script


def _run(**env):
    base = {"PATH": os.environ["PATH"], "LIMIT": "1", "OFFSET": "0", "SCOPE": ""}
    return subprocess.run(["bash", str(SCRIPT)], env={**base, **env}, capture_output=True, text=True, timeout=30)


def test_runner_script_rejects_bad_inputs_before_running_anything():
    assert "unknown source" in _run(SOURCE="rm -rf").stdout
    assert "whole number" in _run(SOURCE="ocga", LIMIT="5 --commit").stdout
    assert "whole number" in _run(SOURCE="ocga", OFFSET="-1").stdout
    assert "YYYY-MM-DD..YYYY-MM-DD" in _run(SOURCE="appeals", SCOPE="2026-01-01;id").stdout
