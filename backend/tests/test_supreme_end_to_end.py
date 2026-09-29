import pytest

from app.ingestion.acquisition import FetchResponse
from app.ingestion.supreme_end_to_end import acquire_discovered_supreme_opinions


PAGE_URL="https://www.gasupreme.us/opinions/september-2026/"
HTML='''
<a href="/wp-content/uploads/2026/09/S26A0123.pdf">S26A0123 Smith v. State</a>
<a href="/wp-content/uploads/2026/09/S26A0456.pdf">S26A0456 Jones v. State</a>
'''


def transport(url: str):
    return FetchResponse(
        url=url,
        status_code=200,
        headers={"content-type":"application/pdf"},
        body=b"%PDF-1.7 official opinion bytes",
    )


def test_discovered_slip_opinions_are_not_indexable_without_real_citation():
    result=acquire_discovered_supreme_opinions(HTML,page_url=PAGE_URL,transport=transport)
    assert result.items==()
    assert len(result.skipped)==2
    assert all("no source-published citation" in row["reason"] for row in result.skipped)


def test_verified_resolver_promotes_acquired_opinion_to_ingestion_item():
    def resolver(document):
        return "321 Ga. 123" if document.external_id=="S26A0123" else None

    result=acquire_discovered_supreme_opinions(
        HTML,page_url=PAGE_URL,transport=transport,citation_resolver=resolver
    )
    assert len(result.items)==1
    assert result.items[0].citation=="321 Ga. 123"
    assert result.items[0].document.external_id=="S26A0123"
    assert len(result.skipped)==1


def test_acquisition_batch_is_bounded():
    result=acquire_discovered_supreme_opinions(
        HTML,page_url=PAGE_URL,transport=transport,citation_resolver=lambda _:"321 Ga. 1",limit=1
    )
    assert len(result.items)==1


def test_rejects_unreasonable_limits():
    with pytest.raises(ValueError):
        acquire_discovered_supreme_opinions(HTML,page_url=PAGE_URL,transport=transport,limit=0)
    with pytest.raises(ValueError):
        acquire_discovered_supreme_opinions(HTML,page_url=PAGE_URL,transport=transport,limit=501)
