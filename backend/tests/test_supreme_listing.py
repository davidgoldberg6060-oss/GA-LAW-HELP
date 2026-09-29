import pytest

from app.ingestion.supreme_listing import discover_supreme_opinions


OFFICIAL_PAGE = "https://www.gasupreme.us/opinions/september-2026/"


def test_discovers_official_https_opinion_links_and_deduplicates():
    html = """
    <a href="/wp-content/uploads/2026/09/S26A0123.pdf">S26A0123 Smith v. State</a>
    <a href="/wp-content/uploads/2026/09/S26A0123.pdf">S26A0123 Smith v. State</a>
    <a href="https://www.gasupreme.us/wp-content/uploads/2026/09/S26A0456.pdf">
      S26A0456 Jones v. State
    </a>
    """

    found = discover_supreme_opinions(html, page_url=OFFICIAL_PAGE)

    assert [item.docket_numbers for item in found] == [("S26A0123",), ("S26A0456",)]
    assert found[0].url == "https://www.gasupreme.us/wp-content/uploads/2026/09/S26A0123.pdf"
    request = found[0].as_request()
    assert request.source_key == "georgia_supreme_court"
    assert request.external_id == "S26A0123"
    assert request.citation is None


def test_rejects_non_official_listing_page():
    with pytest.raises(ValueError):
        discover_supreme_opinions("<a href='/x'>S26A0123 Example</a>", page_url="https://example.com/opinions")


def test_ignores_external_insecure_and_non_docket_links():
    html = """
    <a href="https://example.com/S26A0123.pdf">S26A0123 External copy</a>
    <a href="http://www.gasupreme.us/S26A0456.pdf">S26A0456 Insecure copy</a>
    <a href="/news.pdf">Court news without docket</a>
    """

    assert discover_supreme_opinions(html, page_url=OFFICIAL_PAGE) == []


def test_preserves_multiple_dockets_in_one_opinion():
    html = '<a href="/combined.pdf">S26A0123, S26A0124 Smith v. State</a>'

    found = discover_supreme_opinions(html, page_url=OFFICIAL_PAGE)

    assert len(found) == 1
    assert found[0].docket_numbers == ("S26A0123", "S26A0124")
    assert found[0].as_request().external_id == "S26A0123,S26A0124"
