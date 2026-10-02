import json
import os

from app.ingestion.import_supreme_opinions import main


def test_commit_without_database_url_does_not_invent_rows(monkeypatch, capsys):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    code = main(["--year", "2025", "--limit", "25", "--commit"])
    captured = capsys.readouterr().out.strip().splitlines()
    payload = json.loads(captured[-1])
    assert code == 2
    assert payload["committed"] is False
    assert payload["attempted"] == 0
    assert payload["succeeded"] == 0
    assert "DATABASE_URL" in payload["skipped_reason"]
    assert os.environ.get("DATABASE_URL") in (None, "")
