# 2026-10-22 Court of Appeals court-rules index checkpoint

DATABASE_URL was unset. Discover-only fetch of the Court of Appeals of Georgia court-rules index (https://www.gaappeals.gov/court-rules/) and robots.txt.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `4bfb1e66e92ed2f3f25a970503f724424fc0e63a3d0104ac8223612695833bb8` | WAF captcha; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `04b9aa997bbfd23df03898e4336ae180596c8b95d24cf57b253f6808bf532282` | Same WAF captcha page |

Raw fetch returned the AWS WAF Human Verification challenge for both. No rule page links were named. Lexis was not opened. These counts are not persisted coverage. No corpus rows written. Not stored rule text and not current-law verification.
