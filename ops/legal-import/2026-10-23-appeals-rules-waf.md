# 2026-10-23 Court of Appeals of Georgia rules index checkpoint

DATABASE_URL was unset. Discover-only raw fetch of https://www.gaappeals.gov/rules/. Both the rules index and robots.txt returned the AWS WAF captcha page (HTTP 405); no rule text was retrieved; not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `fd81368fa8330b904f8ae1ad4d0d9726536f9b9f856bc30ceb5ab64361ac4e03` | AWS WAF captcha page; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `c77ae1ec4f48588c7ba32cfae55137a47b9840ba684dd5e5db3cd146e51eb0d2` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No rule HTML or PDF links were named. Lexis was not opened. These counts are not persisted coverage. No corpus rows written. Prior checkpoints noted the same WAF behavior for opinion-search and rules pages.
