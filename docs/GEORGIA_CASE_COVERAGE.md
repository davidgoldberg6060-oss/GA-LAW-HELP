Last production check: 2026-10-15 01:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia opinion-search page and robots.txt. Both returned the AWS WAF captcha page (HTTP 405, x-amzn-waf-action: captcha); not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search page | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `d4e5dbbd5b67fecf55e1d3c14cd635698eb510b4dc5e6a61792a3bf9473b5f2e` | WAF captcha; no index labels |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `d4e5dbbd5b67fecf55e1d3c14cd635698eb510b4dc5e6a61792a3bf9473b5f2e` | Same captcha body |

No docket labels or PDF links were present. Date-window search and efast PDFs were not requested. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15-appeals-opinion-search-index.md`.

