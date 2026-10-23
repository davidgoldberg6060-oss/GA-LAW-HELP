# 2026-10-23 Court of Appeals opinion-search index checkpoint

DATABASE_URL was unset. Discover-only fetch of the Court of Appeals of Georgia opinion-search page (https://www.gaappeals.gov/opinion-search/) and robots.txt. Both returned the AWS WAF Human Verification captcha (HTTP 405). No opinion PDFs or docket-labeled links were retrieved. Not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `1cffc011a4465c8e4d7b5e80fdb44783d3bdf68d408f72baf78810aaca2bec5b` | WAF captcha page; not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `c7c539ffc0d5c141d8156985900c22a6179a038e5dd727763c69f14acff0f9ac` | Same WAF captcha page |

Raw fetch returned the AWS WAF challenge. No docket-labeled PDF anchors were named. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
