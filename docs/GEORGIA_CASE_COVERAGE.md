Last production check: 2026-10-15 10:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only attempt on Georgia Court of Appeals rules and opinion search indexes. Direct fetch blocked by AWS WAF captcha (HTTP 405); no rule or opinion files downloaded; not stored text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | n/a | n/a | WAF captcha; robots.txt allows most paths |
| opinion search | https://www.gaappeals.gov/opinion-search/ | 405 | n/a | n/a | Interactive form; WAF captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 200 | ~70 | n/a | Disallows only /wp-admin/ |

A prior non-automated fetch observed Rules 1-8 stating effective March 26, 2026 and a Spanish complete-rulebook PDF link. Opinion search points to a separate Docket/Case Inquiry System. No PDFs fetched. Lexis was not opened. These counts are not persisted coverage. The gap notes are in `ops/legal-import/2026-10-15-coa-rules-gap.md`.

