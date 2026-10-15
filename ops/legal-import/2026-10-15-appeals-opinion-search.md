# Court of Appeals opinion-search index checkpoint (2026-10-15)

DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinions and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `902bf450208f3400629813ef627e868b0a32f29369eea164d2ce73145caf1b9f` | AWS WAF captcha (Human Verification); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `cc626bceeab4c9ac7fe73e52bc8df9f3dbe8f8199e77342d59030a34293f89ea` | Same WAF captcha page |

Both responses are the CloudFront/AWS WAF Human Verification page (`x-amzn-waf-action: captcha`). No docket-labeled PDF links were named. The importer's date-search endpoint and efast.gaappeals.gov PDFs were not requested. Lexis was not opened. These counts are not persisted coverage. Gap: index page blocked by WAF; no stored Court of Appeals opinion text.
