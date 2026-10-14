# Court of Appeals rules index discover-only (2026-10-14)

DATABASE_URL was unset, so no corpus rows were written.

Fetch of https://www.gaappeals.gov/court-rules/ and https://www.gaappeals.gov/robots.txt both returned an AWS WAF human-verification captcha page (HTTP 405 on HEAD, body 2,511 bytes). No rule index content, no individual rule pages, and no rule text were obtained. Not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `98e77c7014241b88af42599b58788e190b410d1cdde9097aad0fae3d662c4b8d` | AWS WAF captcha; no index content |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `bfdc473a6d84b319112848ce74606eecd96985d980c87a949401a1e14eb7b5d1` | Same captcha page |

Lexis was not opened. These counts are not persisted coverage. Gap: Court of Appeals rules index remains unfetched due to WAF; operator may need a browser session or alternative official source.
