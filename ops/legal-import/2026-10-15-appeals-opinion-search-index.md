# Court of Appeals of Georgia opinion-search index checkpoint (2026-10-15)

Discover-only. DATABASE_URL was unset; no corpus rows written. No opinion PDFs downloaded. Lexis not opened.

## Fetch

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search page | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `d4e5dbbd5b67fecf55e1d3c14cd635698eb510b4dc5e6a61792a3bf9473b5f2e` | AWS WAF captcha page (x-amzn-waf-action: captcha); not the index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `d4e5dbbd5b67fecf55e1d3c14cd635698eb510b4dc5e6a61792a3bf9473b5f2e` | Same captcha body; robots content not obtained |

Both responses are the Human Verification captcha HTML (title "Human Verification", includes awsWafCookieDomainList and challenge.js). No docket labels, no PDF links, and no search form were present in the body. The importer's `discover_index` would record the same WAF gap.

## Gaps

- Index labels and searchable opinion list are behind captcha; not obtained.
- Date-window search endpoint was not called.
- efast.gaappeals.gov PDFs were not fetched.
- Not stored opinion text and not current-law verification.
- These counts are not persisted coverage.

See also `backend/app/ingestion/import_appeals_opinions.py` (`discover_index` / `_checkpoint_page`).
