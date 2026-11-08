"""Regression checks for the static web server config (nginx.web.conf)."""
import re
from pathlib import Path

CONF = (Path(__file__).resolve().parents[1] / "nginx.web.conf").read_text()
SECURITY = ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"]


def _block(start: str) -> str:
    i = CONF.index(start)
    depth = 0
    for j in range(CONF.index("{", i), len(CONF)):
        depth += {"{": 1, "}": -1}.get(CONF[j], 0)
        if depth == 0:
            return CONF[i : j + 1]
    raise AssertionError(start)


def test_manifest_served_as_manifest_json_and_inherits_headers():
    b = _block("location = /manifest.webmanifest")
    assert "default_type application/manifest+json" in b
    assert "add_header" not in b  # keep server-level security headers


def test_service_worker_not_immutable_and_keeps_security_headers():
    b = _block("location = /sw.js")
    assert 'Cache-Control "no-cache"' in b and "immutable" not in b
    for h in SECURITY:
        assert h in b


def test_static_assets_keep_security_headers():
    b = _block("location ~* \\.(?:js|css")
    for h in SECURITY:
        assert h in b
