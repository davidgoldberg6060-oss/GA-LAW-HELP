Last production check: 2026-10-29 23:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only attempt to read the Court of Appeals of Georgia opinion search index. Request blocked by AWS WAF captcha (CloudFront HTTP 405); challenge page hashed; no opinion text, PDFs, or search results retrieved; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion search (raw) | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a743a153b0b0566b55c727eee1b08c769dde9417b2cdc971dafbfb9e3bd21cef` | AWS WAF captcha challenge via CloudFront; x-amzn-waf-action: captcha; no index content |

The official opinion search page is protected by a human-verification captcha. No PDFs or searchable opinion indexes were downloaded. Lexis was not opened. These counts are not persisted coverage. Preferred bulk sources for appellate opinions remain CourtListener and official court sites when accessible without captcha. No corpus coverage claimed.
