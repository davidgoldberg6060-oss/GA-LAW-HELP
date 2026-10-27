# 2026-10-27 Court of Appeals opinion search and rules index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only attempts to fetch the Court of Appeals of Georgia opinion search index and rules index. Both returned AWS WAF/CloudFront captcha challenge pages (HTTP 405, content-length 2511). No opinion or rule text, PDFs, or indexes were retrieved. Lexis was not opened. This is not stored opinion or rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion search | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `6e7ca7453976a37958e2bf8be13988d4d82977808ae86ff38a8da8dfd56b1766` | AWS WAF captcha challenge page; no content; no .pdf or /wp-content/uploads/ |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `e26015e979b9884f402ebfa6b45e26ef466c64203f2710e26557346885c215fc` | AWS WAF captcha challenge page; no content; no .pdf or /wp-content/uploads/ |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `8f2d122df1d485ffc32b9c6c0c6b163e361a79721341ae4789914624d4784ee1` | Same captcha challenge; robots not retrieved |

Gap notes: Automated inventory of the official Court of Appeals opinion search (https://www.gaappeals.gov/opinion-search/) and rules (https://www.gaappeals.gov/rules/) is currently blocked by CloudFront AWS WAF captcha. No PDF anchors or rule text could be counted. Docket search at https://www.gaappeals.gov/docket-search/ is similarly protected. These counts are not persisted coverage. Preferred future access may require browser-based or authorized session after captcha. No corpus rows written.
