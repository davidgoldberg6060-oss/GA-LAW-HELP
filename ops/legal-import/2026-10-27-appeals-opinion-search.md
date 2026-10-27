# 2026-10-27 Court of Appeals opinion-search checkpoint

Fetch date: 2026-10-27 16:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals of Georgia opinion-search index and robots.txt. No opinion PDFs, orders, or text files were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `19ffe132a7d144ee14fcdd6536efeba5c127d01d2807a5278089985c2afab71c` | AWS WAF Human Verification / captcha page (x-amzn-waf-action: captcha); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `5d022b9008d8785cc18148c88b2c82cb07591a9f5ee0363ac8cd6e69a75ed599` | Same WAF captcha page |

Raw non-browser fetch of both URLs returned the AWS WAF Human Verification challenge page (HTTP 405). A separate browser-rendered fetch of the same opinion-search URL succeeded and showed a date-range search form linking to the docket search, but no PDF anchors or opinion text were extracted or stored. No date-search endpoint was called. Prior 2026-10-15 checkpoint also recorded HTTP 405 WAF for these URLs (different captcha hashes). Lexis was not scraped.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. These counts are not persisted coverage.
