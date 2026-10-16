# Court of Appeals rules pages — discover-only WAF checkpoint

**Date:** 2026-10-16 07:01 UTC
**DATABASE_URL:** unset (no corpus rows written)

Raw fetch of Court of Appeals rules index and sample rules page returned AWS WAF captcha (HTTP 405). No rule text was extracted or stored. Not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `61c944bfd27c54635cf43ec1b41adf5be88deaabe915aba0f17a1cc87d52ad64` | WAF captcha |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `b3bde0399c2932e8526799f26170298e0755cbe0c30a93f4b3630fde0ad99819` | WAF captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `7c988552f39fdedd431795b602137ab985d9ea13d056d809ec4de497d8e35cb8` | Same WAF page |

A browser-based fetch of https://www.gaappeals.gov/rules-1-8/ returned the published rules text (effective March 26, 2026) including Rule 1–8 general provisions. That text was not persisted. Lexis was not opened. These counts are not persisted coverage.
