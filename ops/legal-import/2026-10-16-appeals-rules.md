# Court of Appeals rules index checkpoint (2026-10-16)

Fetch date: 2026-10-16 13:02 UTC. DATABASE_URL is unset. No rule pages or PDFs were downloaded beyond the WAF response. No authority rows were written. This is not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `250c72a072c5a247e052146e60c5929b5d4af960640581e016be756ef52858aa` | AWS WAF captcha; not a rules index |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `5eb9ae13be78f8a67812f4f8724dec20c802526487431ab7dfab91d0b5bcf09e` | AWS WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6bed2fb82f90f8a01003e33310e250285736dd6e253b4a4042b58b2cfa436458` | Same WAF captcha page |

Raw fetch of the rules index, a representative section page (rules-1-8), and robots.txt each returned the AWS WAF Human Verification challenge (HTTP 405, 2,511 bytes). Captcha page hashes differ across requests. No rule text or PDF anchors were obtained. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the WAF-blocked index only. Court of Appeals rule text remains unfetched. Missing DATABASE_URL means no corpus rows can be written. Currency is unknown. Prior opinion-search checkpoint also recorded WAF.
