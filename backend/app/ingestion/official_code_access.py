"""Official access notes for unannotated OCGA text.

The Georgia General Assembly navigation item labeled Georgia Code points at a
LexisNexis host. That host is annotations territory and must not be fetched.
The General Assembly ``/laws`` path is an application shell, not statute text.
Session-law search counts are currency-gap notes against the 2022-11 release;
they are not stored authorities.
"""
from __future__ import annotations

from urllib.parse import urlparse

LEXIS_CODE_URL = "http://www.lexisnexis.com/hottopics/gacode"
LEGIS_LAWS_URL = "https://www.legis.ga.gov/laws"
LEGIS_SEARCH_URL = "https://www.legis.ga.gov/search"
SIGNED_BY_GOVERNOR_URL = "https://www.legis.ga.gov/legislation/signed-by-governor"
RELEASE_AS_OF = "2022-11"


def is_lexis_code_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return host == "www.lexisnexis.com" or host.endswith(".lexisnexis.com") or "lexis" in host


def refuse_lexis_code_url(url: str) -> None:
    """Block any fetch of the publisher code site. Annotations are not inventoried."""
    if is_lexis_code_url(url):
        raise ValueError("Refusing Lexis code URL; do not scrape annotations or publisher text")


def currency_gap() -> dict:
    """Checkpoint facts only. Does not claim stored sections or current law."""
    return {
        "mode": "discover-only",
        "committed": False,
        "release_as_of": RELEASE_AS_OF,
        "official_code_link": LEXIS_CODE_URL,
        "official_code_link_opened": False,
        "legis_laws_url": LEGIS_LAWS_URL,
        "legis_laws_note": "HTML shell only; client route /laws returned page-not-found. Not statute text.",
        "signed_by_governor_url": SIGNED_BY_GOVERNOR_URL,
        "signed_by_governor_result_label": "Showing Results 1-20 of 742",
        "signed_by_governor_scope": "2025-2026 Regular Session (Current), status Signed By Governor",
        "gap": (
            "742 is a rendered search-result label, not a stored act count and not proof each act amends the OCGA. "
            "No bill text downloaded. release86.2022.11 remains unverified for currency."
        ),
    }
