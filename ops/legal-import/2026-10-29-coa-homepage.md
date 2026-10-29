# 2026-10-29 Court of Appeals homepage checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Court of Appeals of Georgia landing page (redirects to docket-search). No opinion PDFs, rules PDFs, or full text were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage (after redirect) | https://www.gaappeals.us/ | 200 | 39,314 | `4c92b0d07ca7b0a76fd30ecdb37fbdfebaa77cb8e4a05685b4768b7f710d3d15` | Title: Docket Search – Court of Appeals of the State of Georgia; links to opinion-search, rules, docket |

The page names an Opinion Search link (https://www.gaappeals.gov/opinion-search/) and rules pages. Subsequent direct fetches to opinion-search and rules returned 405 (CloudFront WAF captcha). robots.txt on gaappeals.us returned 404. No corpus coverage claimed. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the public landing page only. Opinion and rule PDFs remain unfetched pending DATABASE_URL and robots/WAF review. Preferred bulk sources for opinions remain prior CourtListener or official PDF indexes where robots allow. Annotations and Lexis not scraped.
