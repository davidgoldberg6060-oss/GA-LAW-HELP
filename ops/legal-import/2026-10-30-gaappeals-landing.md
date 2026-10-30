# 2026-10-30 Court of Appeals of Georgia landing checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Court of Appeals landing page via the redirect host. No opinion PDFs, rules PDFs, or docket documents were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| landing (via redirect) | https://links.gaappeals.us (redirect from https://www.gaappeals.us/) | 200 | 39,314 | `4c92b0d07ca7b0a76fd30ecdb37fbdfebaa77cb8e4a05685b4768b7f710d3d15` | Page titled Docket Search; links to https://www.gaappeals.gov/opinion-search/ and /rules-1-8/; no PDFs named or fetched |
| opinion-search (direct) | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `ac3b76488a2caeb8b5ce3595721d502e76deab5e69fd459cd14c35ca1f375847` | AWS WAF Human Verification captcha; same as 2026-10-15 |
| homepage (direct) | https://www.gaappeals.gov/ | 405 | 2,511 | (same captcha) | WAF blocks non-browser clients |

The landing page names Opinion Search and Court Rules links under gaappeals.gov, which remain behind WAF. No PDF anchors were extracted or downloaded. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the accessible landing redirect and confirmed WAF on the primary domain. Court of Appeals opinions and rules remain unfetched from non-browser clients. Missing DATABASE_URL means no corpus rows can be written. Preferred path for future import remains browser-capable or alternative official bulk sources once access is confirmed.
