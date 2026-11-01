from app.ingestion import import_court_rules as m


def test_save_then_replay_roundtrip(tmp_path):
    def fake(url, limit):
        return m.Fetched(url, "text/html", b"<p>official</p>")
    saved = m.saving_fetch(fake, str(tmp_path))
    assert saved("https://www.gaappeals.gov/court-rules/", 1000).body == b"<p>official</p>"
    replay = m.replay_fetch(str(tmp_path))
    got = replay("https://www.gaappeals.gov/court-rules/", 1000)
    assert got.body == b"<p>official</p>" and got.content_type == "text/html"


def test_replay_missing_is_404(tmp_path):
    import urllib.error
    import pytest
    with pytest.raises(urllib.error.HTTPError):
        m.replay_fetch(str(tmp_path))("https://www.gaappeals.gov/x/", 1000)
