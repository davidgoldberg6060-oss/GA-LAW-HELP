# 2026-10-29 Court of Appeals accessible entry-point checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Court of Appeals of Georgia public entry point. No opinion PDFs, rules PDFs, or other document files were downloaded. Lexis was not opened. This is not stored opinion or rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| entry redirect | https://www.gaappeals.us/ | 302 | (redirect) | n/a | Location: https://links.gaappeals.us |
| docket-search index (followed) | https://links.gaappeals.us/ (via redirect) | 200 | 39,314 | `4c92b0d07ca7b0a76fd30ecdb37fbdfebaa77cb8e4a05685b4768b7f710d3d15` | Title: Docket Search – Court of Appeals of the State of Georgia; names Opinion Search, Court Rules, Docket Search |
| opinion-search (direct) | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | (WAF captcha page; hash varies) | AWS WAF Human Verification; no index content |
| robots / direct pages | https://www.gaappeals.gov/ | 405 | ~2,511 | (WAF) | Direct domain remains WAF-blocked for non-browser clients |

The accessible entry via gaappeals.us redirects to a page that presents the Docket Search interface and links to Opinion Search and Court Rules. Direct requests to gaappeals.gov paths return the WAF captcha (consistent with the 2026-10-15 checkpoint). No PDF anchors were extracted or downloaded from the followed page. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the accessible entry-point HTML and confirmation that opinion-search and rules indexes remain behind WAF for automated clients. Preferred path for future import remains browser-capable or alternative official channels once DATABASE_URL is set and reviewed. Missing DATABASE_URL means no corpus rows can be written.
