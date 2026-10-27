# 2026-10-27 Court of Appeals opinion-search WAF checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the official Court of Appeals opinion-search index and robots.txt. Both returned the AWS WAF Human Verification challenge (HTTP 405). No opinion PDFs, dockets, or rule texts were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `9d0addae10d0b33d6c5e2a3a6b2fe2b31fd3979f531350a0a7227ee675d46884` | WAF captcha page (Human Verification); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `45d83b84606250f71823e88c68a7e7e4a9f27913b01f725f319d65381c38f5d8` | Same WAF captcha response |

Raw fetches returned the challenge page. No docket-labeled PDF links were named or downloaded. The date-search endpoint was not called. These counts are not persisted coverage. No authority rows written.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Prior 2026-10-15 checkpoint recorded a different WAF hash for the same URLs. Preferred path remains browser or official bulk sources once accessible. Annotations remain editorial and are not scraped.
