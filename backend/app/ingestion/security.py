from urllib.parse import urlparse

ALLOWED_HOSTS = {
    "www.gasupreme.us", "gasupreme.us",
    "www.gaappeals.us", "gaappeals.us",
    "georgiacourts.gov", "www.georgiacourts.gov", "assets.georgiacourts.gov",
    "www.legis.ga.gov", "legis.ga.gov",
}

def assert_public_official_url(url: str) -> str:
    p = urlparse(url)
    if p.scheme != "https":
        raise ValueError("Only HTTPS official sources are permitted")
    host = (p.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise ValueError(f"Host not allowlisted: {host}")
    if p.username or p.password:
        raise ValueError("Credential-bearing URLs are prohibited")
    return url
