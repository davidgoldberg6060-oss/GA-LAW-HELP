# Court of Appeals opinion-search index checkpoint (2026-10-15)

Fetch date: 2026-10-15 22:00 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a60e59e2e67412d10f9968a360c89a48e30fec247553546c59d17638a0c444c4` | WAF captcha (Human Verification / awsWafCookieDomainList); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6f6c93f471077686c272395d6325401e3b5a5ff08eef110b11b082ad109867cb` | Same WAF captcha page |

Raw fetch of both URLs returned the AWS WAF Human Verification challenge page (HTTP 405). No docket-labeled PDF links were named or downloaded. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Prior 2026-10-08 note also recorded HTTP 405 for Court of Appeals opinion search and rules indexes.
