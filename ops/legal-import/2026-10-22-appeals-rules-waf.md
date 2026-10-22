Last production check: 2026-10-22 21:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals rules index and robots.txt. Both returned the AWS WAF captcha; no rule PDFs or text were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `8947935b3858c2cf17ee1aaaccef15703d8a78123fc110d25ead4ea7c3e76c0d` | WAF captcha; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `d75e4877b8a8702d81a4afeff37eef67dd7f451c44b722c7febb8a2167e8d3f5` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No PDF anchors were named. Lexis was not opened. These counts are not persisted coverage. Prior 2026-10-15 opinion-search checkpoint also saw WAF (different hashes). Court of Appeals rules and opinion indexes remain inaccessible via raw fetch.
