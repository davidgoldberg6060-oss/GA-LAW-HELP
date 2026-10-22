Last production check: 2026-10-22 15:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia court-rules index and robots.txt. Both returned the AWS WAF captcha (HTTP 405); rule pages were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `4bfb1e66e92ed2f3f25a970503f724424fc0e63a3d0104ac8223612695833bb8` | WAF captcha; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `04b9aa997bbfd23df03898e4336ae180596c8b95d24cf57b253f6808bf532282` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No rule page links were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-appeals-court-rules.md`.

The complete prior coverage ledger (through 2026-10-22 06:00 UTC OCGA manifest checkpoint) is unchanged from main. DATABASE_URL remains unset; no corpus coverage is claimed.
