# Court of Appeals of Georgia opinion-search index checkpoint (2026-10-14)

DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the public opinion-search page and robots.txt. No date-search endpoint was requested and no opinion PDFs were downloaded. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `b9bfa2160dadbdaf7732120c98d5c7e8c76a271715e0b4ad7ace1440ea3ab4ff` | AWS WAF captcha ("Human Verification"); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `5b9962f521630cecd46543b36a33b8b78a4247ec01024d011cba94f4d745e11b` | Same captcha response; not the robots policy |

The fetch returned the CloudFront/AWS WAF captcha challenge (x-amzn-waf-action: captcha) for both URLs. No docket labels or PDF links were visible. The date-search results endpoint was not requested. Lexis was not opened. These counts are not persisted coverage. The gap (WAF block) is the same as earlier 2026-10-09 checkpoints; the response bytes and hash differ.
