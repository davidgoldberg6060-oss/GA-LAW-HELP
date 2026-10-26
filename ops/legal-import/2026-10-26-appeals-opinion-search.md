# Court of Appeals opinion-search index checkpoint (2026-10-26)

Fetch date: 2026-10-26 11:01 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `03bfda869ef48fb32f0051201ff221c36484ae51a6a9c4d962817799673337ab` | WAF captcha (x-amzn-waf-action: captcha); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | (same captcha family) | Same WAF captcha page |

Raw fetch of both URLs returned the AWS WAF Human Verification challenge page (HTTP 405, content-length 2511). No docket-labeled PDF links were named or downloaded. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Prior 2026-10-15 note recorded a different captcha hash (`a60e59e2...`).
