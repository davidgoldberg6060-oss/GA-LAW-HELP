# 2026-10-22 Court of Appeals rules index checkpoint

DATABASE_URL was unset. Discover-only raw fetch of the Court of Appeals rules index and robots.txt.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `302a4015525b326f4351e13e23b7c26139310da172dfcc19db55117e44374005` | AWS WAF captcha (x-amzn-waf-action: captcha); not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `11a24eff0a3ce408e35272a710288d069ecc274deabcbe32e33349b38a2db271` | Same WAF captcha page |

Raw curl returned the Human Verification challenge. No PDF or rule-text links were named. Opinion-search endpoint was not called in this pass. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
