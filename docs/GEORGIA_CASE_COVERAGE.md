Last production check: 2026-10-16 13:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals rules index, a section page, and robots.txt. All returned the AWS WAF captcha; no rule text was obtained; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `250c72a072c5a247e052146e60c5929b5d4af960640581e016be756ef52858aa` | WAF captcha; not a rules index |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `5eb9ae13be78f8a67812f4f8724dec20c802526487431ab7dfab91d0b5bcf09e` | WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6bed2fb82f90f8a01003e33310e250285736dd6e253b4a4042b58b2cfa436458` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge for each. No rule text or PDF links were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-appeals-rules.md`.

