Last production check: 2026-10-14 14:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only attempt on the Georgia Court of Appeals opinion search (https://www.gaappeals.gov/opinion-search/). Page bytes were hashed; no opinion text was read; not stored opinions and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `07803c75212674308ce5a1669f63abccad28cc7c9650fad8b5471dd37417a90f` | AWS WAF captcha challenge |
| home | https://www.gaappeals.gov/ | 405 | 2,511 | `7f95dd9ec821b326c5951db3479448bad43ad6260d263b5d8fabb802f852afb0` | AWS WAF captcha challenge |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `416a4a08a639c72e29b1f269dea0a9b668eb7fa7287ca2e6235932cc253782db` | AWS WAF captcha challenge |

The Court of Appeals site (moved from gaappeals.us) is behind an AWS WAF captcha. Automated fetches receive only the challenge page. No opinion indexes or PDFs were retrieved. Prior note from 2026-10-08 recorded HTTP 405 on the old domain. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-14-coa-opinion-search.md`.

