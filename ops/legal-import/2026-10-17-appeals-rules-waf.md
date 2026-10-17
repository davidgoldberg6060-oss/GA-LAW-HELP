# Court of Appeals rules pages checkpoint (2026-10-17)

Fetch date: 2026-10-17 16:01 UTC. DATABASE_URL is unset. No rule PDFs or HTML text were stored as authority. No authority rows were written. This is not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index (raw) | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `2845e116ef40ac860f3565c5e64a9a3d8dc9bff98c84d4e6d97f0afc6b5e8345` | AWS WAF captcha; not rule text |
| robots.txt (raw) | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `d1b7ae7186c136c1f28dbe8f2e6b90fe883c932a263e7367a2bcc0506f1e6587` | Same WAF captcha page |
| rules-1-8 (raw) | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | (same captcha pattern) | WAF; browser-rendered pages exist |

Raw HTTP fetches (curl) return the AWS WAF Human Verification captcha (HTTP 405, ~2511 bytes). Browser-rendered access shows Court of Appeals Rules pages (e.g. Rules 1-8: General) stating the rules are effective on March 26, 2026. No PDFs were downloaded. Lexis was not opened. These counts are not persisted coverage.

Gap notes: direct crawler access remains blocked by WAF. Rule text is visible in browser but not fetched or stored here. Missing DATABASE_URL means no corpus rows can be written. Currency is unknown pending later official comparison.
