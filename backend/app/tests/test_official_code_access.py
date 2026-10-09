from backend.app.ingestion.official_code_access import (
    LEXIS_CODE_URL,
    currency_gap,
    refuse_lexis_code_url,
)


def test_lexis_code_link_is_refused():
    try:
        refuse_lexis_code_url(LEXIS_CODE_URL)
    except ValueError as exc:
        assert "Lexis" in str(exc)
    else:
        raise AssertionError("Lexis code URL must be refused")


def test_currency_gap_is_not_stored_coverage():
    gap = currency_gap()
    assert gap["committed"] is False
    assert gap["official_code_link_opened"] is False
    assert gap["release_as_of"] == "2022-11"
    assert "not a stored act count" in gap["gap"]
