"""Bounded HTTPS transport for official Georgia legal acquisition."""
from __future__ import annotations

import urllib.error
import urllib.request

from .acquisition import FetchResponse, MAX_DOCUMENT_BYTES
from .security import assert_public_official_url

USER_AGENT = "GA.LAW.HELP-LegalCorpus/1.0"
TIMEOUT_SECONDS = 15


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    """Validate every redirect hop before urllib follows it."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe = assert_public_official_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, safe)


def production_transport(url: str) -> FetchResponse:
    safe_url = assert_public_official_url(url)
    opener = urllib.request.build_opener(_SafeRedirect())
    request = urllib.request.Request(
        safe_url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,application/xhtml+xml,application/pdf"},
        method="GET",
    )
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            # Read at most one byte beyond the ingestion ceiling so oversized
            # responses are detected without buffering an unbounded body.
            body = response.read(MAX_DOCUMENT_BYTES + 1)
            return FetchResponse(
                url=response.geturl(),
                status_code=getattr(response, "status", 200),
                headers=dict(response.headers.items()),
                body=body,
            )
    except urllib.error.HTTPError as exc:
        body = exc.read(MAX_DOCUMENT_BYTES + 1) if exc.fp else b""
        return FetchResponse(
            url=exc.geturl() or safe_url,
            status_code=exc.code,
            headers=dict(exc.headers.items()) if exc.headers else {},
            body=body,
        )
