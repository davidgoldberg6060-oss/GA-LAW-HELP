# Court of Appeals opinion-search index checkpoint (2026-10-29)

Fetch date: 2026-10-29 13:02 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `b09e908b8b345e72f05922a613ccbbc2e2c42d9a495cd6b10fcc8a17ef0164f6` | AWS WAF Human Verification captcha page (x-amzn-waf-action: captcha); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `e1fd777ded4530251777852cab742d4233e1d30e0c06638a314b94a69c759ea0` | Same WAF captcha page |

Raw fetch of both URLs returned the AWS WAF Human Verification challenge page (HTTP 405, 2511 bytes). No docket-labeled PDF links were named or downloaded. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Prior 2026-10-15 checkpoint recorded a different hash for the same WAF page.
