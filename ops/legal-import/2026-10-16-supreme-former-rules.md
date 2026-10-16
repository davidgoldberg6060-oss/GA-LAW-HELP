# Supreme Court former-rules HTML checkpoint (2026-10-16)

Fetch date: 2026-10-16 23:01 UTC. DATABASE_URL is unset. No rule PDFs were downloaded. No authority rows were written. This is not stored current rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| former-rules HTML | https://www.gasupreme.us/rules/former-rules/ | 200 | 1,698,294 | `4dc4d51abf7fd05e81e8713eb602ddb174bd5ce79456668aa0fa3d790f3c72f5` | ~121 unique Rule N labels; HTML text of former rules |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The page is titled "Former Rules Of The Supreme Court Of Georgia" and states the Court Rules were amended on January 1, 2024; current rules are elsewhere. It contains HTML text of prior rules (office hours, filings, appeals, etc.) with some cross-links. Two PDF links appear (current rules PDF and a certificate template); neither was fetched because robots.txt disallows `/wp-content/uploads/`. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch (HTTP 405, ~2,511-byte captcha). These counts are not persisted coverage.

Gap notes: inventory of the former-rules HTML only. Current rules PDF and order PDFs remain unfetched. Missing DATABASE_URL means no corpus rows can be written. This page is explicitly former/superseded text; currency of any rule is unknown pending later official comparison against the current rules PDF.
