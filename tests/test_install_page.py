"""Phone install page: real APK link, honest iPhone steps, served at /install, not cached as the app shell."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "public/install.html").read_text()
CONF = (ROOT / "nginx.web.conf").read_text()
SW = (ROOT / "public/sw.js").read_text()


def test_android_link_points_at_signed_release_asset():
    assert "https://github.com/davidgoldberg6060-oss/GA-LAW-HELP/releases/download/apk-1.7.3-release/ga-law-help-1.7.3-release.apk" in PAGE


def test_iphone_steps_are_home_screen_web_app_not_app_store():
    for step in ("Safari", "Share", "Add to Home Screen", "Open as Web App", "Add"):
        assert step in PAGE
    assert "no App Store app" in PAGE
    assert "internet" in PAGE


def test_page_is_accessible_basics_and_script_free():
    assert '<html lang="en">' in PAGE and 'name="viewport"' in PAGE
    assert "<script" not in PAGE  # CSP allows no inline scripts


def test_served_at_install_route():
    assert "location = /install {" in CONF and "try_files /install.html =404;" in CONF


def test_service_worker_only_caches_root_as_app_shell():
    assert "url.pathname==='/'" in SW
