from backend.app.authority_search_service import search_terms


def test_natural_question_keeps_legal_keywords_not_the_whole_sentence():
    terms = search_terms("what happens if you are charged for murder")
    assert "murder" in terms
    assert "what" not in terms
    assert "happens" not in terms
    assert "charged" not in terms


def test_stopwords_only_do_not_match_everything():
    assert search_terms("what happens if you are") == []


def test_citation_like_token_is_kept():
    assert "299-ga-1" in search_terms("is 299-Ga-1 still good law")
