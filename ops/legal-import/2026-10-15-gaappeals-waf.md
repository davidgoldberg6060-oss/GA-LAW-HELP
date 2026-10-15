# 2026-10-15 Court of Appeals index WAF checkpoint

DATABASE_URL was unset. No opinion, rule, or other document was downloaded and no corpus rows were written.

Discover-only fetch of Georgia Court of Appeals public index pages. All three returned HTTP 405 with an AWS WAF Human Verification (captcha) interstitial. Page bytes were hashed; no underlying HTML, opinion PDFs, or rule text was retrieved.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `9cbafde505256a4a8dd515166fde21784b213f3c1f80201cab5880bb4d3b0e60` | AWS WAF captcha interstitial only |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `5e3ebf00867df952169baba8194d960338d821cb31d1e826a9960968def88c77` | AWS WAF captcha interstitial only |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `21ce09c589ac6d23e9764d655449823efc7fba2c27d64c42b38a9182fcb6d2b8` | AWS WAF captcha interstitial only |

Gap notes: raw fetch blocked by WAF captcha (same pattern noted on 2026-10-08 and in the 2026-10-15 OCGA checkpoint). No docket labels, opinion links, or rule text were observed. Not stored appellate opinions or rules and not current-law verification. Lexis was not opened. These counts are not persisted coverage.
