# 2026-10-28 Court of Appeals opinion search index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Georgia Court of Appeals opinion search page (https://www.gaappeals.gov/opinion-search/). Raw response was an AWS WAF captcha challenge page (HTTP 405, 2,511 bytes); no opinion index content, PDF anchors, or opinion text was retrieved. robots.txt request returned the same captcha page. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion search (challenge) | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `65bc3127dc7649677d4e6d67cde793e31d0caf2223efd141ba1a6f9704afbbef` | AWS WAF captcha HTML; x-amzn-waf-action: captcha; no index or opinions |
| robots.txt (challenge) | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `8eabaf12719857c91da1063338f4ed4953e7d6b9cea5da4cbbd6b955a2aabba4` | Same captcha page |

The official opinion search endpoint is behind a captcha. No opinions were downloaded. These counts are not persisted coverage. Gap notes: captcha blocks automated inventory of the index; future import requires human-assisted access or official bulk feed if available. Preferred sources for opinions remain public domain archives or court-provided bulk where licensed for free reuse. No private case data published.
