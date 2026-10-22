# Court of Appeals home page checkpoint (2026-10-22)

Fetch date: 2026-10-22 22:01 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| home page | https://www.gaappeals.gov/ | 405 | 2,511 | `8d305a4174fa42014358f1fec3a2357df8eea76c5ac17f1b70cac00f813dfb25` | WAF captcha (Human Verification); not the court home content |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `3a7222e0a11de818045cb151f7d944b507eabccba51bcaa16e3f9a5c4c07cdb7` | Same WAF captcha page |

Raw fetch of both URLs returned the AWS WAF Human Verification challenge page (HTTP 405). No docket-labeled PDF links were named or downloaded. Opinion-search and rules indexes were not re-fetched in this pass (prior checkpoints show the same WAF block). Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes, rules, and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Prior 2026-10-15 checkpoint recorded the same HTTP 405 for opinion-search.
