# 2026-10-26 Court of Appeals opinion-search index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Georgia Court of Appeals opinion-search index and robots.txt. Both returned AWS WAF captcha challenge pages (HTTP 405). No opinion PDFs or docket indexes were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `3973290dfc39a71ba121a66fd018b0dfe2cc7c99361fa75e8813cf7470860864` | WAF captcha (Human Verification / awsWafCookieDomainList); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `783d69af35b8531586489cff34e029ce14b27f304e4867548748f7ee115c4a6f` | Same WAF captcha page |

Raw fetch of both URLs returned the AWS WAF Human Verification challenge page (HTTP 405, CloudFront). Hashes differ from the 2026-10-15 checkpoint. No docket-labeled PDF links were named or downloaded. The date-search endpoint was not called. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Prior 2026-10-15 and 2026-10-08 notes also recorded HTTP 405 for Court of Appeals opinion search and rules indexes. Preferred public bulk opinion sources remain Free Law Project / CourtListener (courts `ga`, `gactapp`) once DATABASE_URL is set.
