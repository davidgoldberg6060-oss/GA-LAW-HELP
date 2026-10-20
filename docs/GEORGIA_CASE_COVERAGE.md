Last production check: 2026-10-20 00:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals rules index and robots.txt. Both returned the AWS WAF Human Verification captcha (HTTP 405, 2,511 bytes); no rule text was downloaded or stored; not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `fe47599f423cc414ce4cc911aa424ecbf7d833940ee3f717fd02cc7c4a80dccc` | WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `7d6e037788f6a2f0adc0c1cce91fc3a645af544fae4222e17c8530e99590325a` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No rule PDFs or HTML rule text were named or fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-20-appeals-rules.md`.

