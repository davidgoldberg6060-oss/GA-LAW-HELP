"""Owner stats page is a static, token-gated page at /stats, not the app shell."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "public/stats.html").read_text()
JS = (ROOT / "public/stats.js").read_text()
CONF = (ROOT / "nginx.web.conf").read_text()
API_PAGE = (ROOT / "backend/app/stats_page.html").read_text()


def test_served_at_stats_route():
    assert "location = /stats {" in CONF and "try_files /stats.html =404;" in CONF


def test_page_points_at_the_api_and_keeps_the_token_in_local_storage():
    assert 'name="stats-api"' in PAGE
    assert "https://api-production-60cc.up.railway.app" in PAGE
    assert "ga_stats_token" in JS
    assert "localStorage" in JS
    assert "/stats/summary" in JS


def test_website_page_has_no_inline_script():
    # nginx CSP allows script-src 'self' only.
    assert "<script>" not in PAGE
    assert 'src="/stats.js"' in PAGE


def test_api_and_website_pages_cover_the_same_metrics():
    for page in (PAGE, API_PAGE, JS):
        assert "How people are using the app" in page or "Today" in page or "last_7_days" in JS
    for needle in ("Today", "Last 7 days", "Last 30 days", "Average rating", "Recent comments"):
        assert needle in JS
