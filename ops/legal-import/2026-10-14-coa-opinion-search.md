# 2026-10-14 Court of Appeals opinion-search checkpoint

DATABASE_URL was unset. No opinion text was downloaded and no corpus rows were written.

Discover-only attempt on the Georgia Court of Appeals opinion search (site moved from gaappeals.us to gaappeals.gov).

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `07803c75212674308ce5a1669f63abccad28cc7c9650fad8b5471dd37417a90f` | AWS WAF captcha challenge page; no index content |
| home | https://www.gaappeals.gov/ | 405 | 2,511 | `7f95dd9ec821b326c5951db3479448bad43ad6260d263b5d8fabb802f852afb0` | AWS WAF captcha challenge page |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `416a4a08a639c72e29b1f269dea0a9b668eb7fa7287ca2e6235932cc253782db` | AWS WAF captcha challenge page (not real robots.txt) |

Gap notes: The entire gaappeals.gov origin returned HTTP 405 with `x-amzn-waf-action: captcha` and a Human Verification challenge page (CloudFront + AWS WAF). No opinion index labels, PDF links, or rule text were readable. Prior 2026-10-08 note recorded HTTP 405 on the old gaappeals.us opinion search and rules indexes. No PDFs fetched. Lexis was not opened. These counts are not persisted coverage and not current-law verification. Official public opinion indexes for the Court of Appeals remain blocked from automated discover-only reads until the WAF challenge can be completed or an alternative public index is identified.
