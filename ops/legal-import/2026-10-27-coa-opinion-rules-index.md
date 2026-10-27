# 2026-10-27 Georgia Court of Appeals opinion-search and rules index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only attempt to fetch the official Court of Appeals opinion-search page, rules index, and homepage. All returned HTTP 405 with CloudFront WAF captcha challenge (x-amzn-waf-action: captcha). Challenge response bytes were hashed; no opinion PDFs, rule PDFs, or statute text were downloaded. Lexis was not opened. This is not stored opinion or rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `ff788173ba10443d401d464526b8ecb4f4c0f8f44970def87a8e89933f19eb9a` | WAF captcha challenge page; no PDF anchors |
| rules | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `b9c7bb983c28c77963d6f5ac0329594288201359b27599a96a05ccd5f9240d7a` | WAF captcha challenge page |
| homepage | https://www.gaappeals.gov/ | 405 | 2,511 | `a75a657817b183544a8427ee592910f193403133e014f1166aaf6c93e925d271` | WAF captcha challenge page |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6a349891e916af3ee1c48972849028588c247c171733d1f8119396b7e58cbfdc` | WAF captcha challenge page |

The official site hosts an opinion search by date and rules (effective March 26, 2026 per public pages). Access is currently gated by AWS WAF captcha. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the blocked endpoints only. Appellate opinion indexes and Court of Appeals rules remain unfetched due to WAF. Preferred bulk sources for opinions continue to include CourtListener (public domain) where available; currency must be verified. No annotations scraped.
