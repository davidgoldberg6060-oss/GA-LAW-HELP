import json

from app.ingestion.import_supreme_opinions import commit_database_ready, main


def test_commit_refuses_when_database_url_missing(monkeypatch, capsys):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert commit_database_ready()
    code = main(["--year", "2025", "--limit", "25", "--commit"])
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["committed"] is False
    assert payload["coverage_recorded"] is False
    assert payload["succeeded"] == 0
    assert "DATABASE_URL" in payload["reason"]


def test_commit_refuses_sqlite_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./ga_law_help.db")
    assert "sqlite" in commit_database_ready()
