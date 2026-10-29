# Court of Appeals opinion-search index checkpoint (2026-10-29)

Fetch date: 2026-10-29 12:00 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `4d50bc2bc1c8fe81a34964596c7c061ba5f7e2ec80c56c2ad349fbc9d540cc61` | AWS WAF Human Verification captcha (awsWafCookieDomainList / challenge.js); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `baa0848d145763f5c975f1495167ef2d7ab772aa2d0f9a28111f125b5f4b0992` | Same WAF captcha page |

Raw fetch of both URLs returned the AWS WAF Human Verification challenge page (HTTP 405). No docket-labeled PDF links were named or downloaded. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Hash differs from the 2026-10-15 checkpoint for the same URLs.
