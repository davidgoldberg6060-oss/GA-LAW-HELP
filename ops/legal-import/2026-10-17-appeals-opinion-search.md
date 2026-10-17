# Court of Appeals opinion-search index checkpoint (2026-10-17)

DATABASE_URL was unset, so no opinion PDFs were downloaded and no authority rows were written.

Discover-only raw fetch of https://www.gaappeals.gov/opinion-search/ and robots.txt on 2026-10-17 ~04:00 UTC.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `b75b9c3e7a6b35a555a5b30ffb2d4f8caa12b9d25611d1b36139a0b52c4c6ae1` | WAF captcha; not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `a755cc6856dea0f4f22d1d159f909e3a09fc1ae4b6ccef31e08c64c23db62b0a` | Same WAF captcha page |

Raw fetch returned the Human Verification / AWS WAF challenge page. No docket-labeled PDF links were named. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage.

Prior checkpoint (2026-10-15) used different captcha hashes for the same byte length.
