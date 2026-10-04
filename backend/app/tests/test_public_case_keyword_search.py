from app.authority_search_service import search_keywords
from app.public_case_service import public_case_keyword_clause


def test_natural_question_is_not_searched_as_one_phrase():
    question = "what happens if you are charged for murder"
    words = search_keywords(question)
    assert "murder" in words
    assert "charged" not in words
    clause = public_case_keyword_clause(question)
    compiled = str(clause.compile(compile_kwargs={"literal_binds": True})).lower()
    assert "%murder%" in compiled
    assert question not in compiled


def test_blank_public_case_query_has_no_keyword_clause():
    assert public_case_keyword_clause("   ") is None
