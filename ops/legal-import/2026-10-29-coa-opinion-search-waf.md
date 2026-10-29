# 2026-10-29 Court of Appeals opinion search access checkpoint

DATABASE_URL is unset, so no authority rows were written and no opinion PDFs or text were downloaded. Discover-only raw fetch of the official Court of Appeals opinion search page returned an AWS WAF human-verification challenge (HTTP 405, 2,511 bytes). Not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion search (raw) | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `7bff1dc0666542933c46c349d4add13c487d86d9385fb8712df39da54eb5a6c9` | AWS WAF captcha challenge page; no opinion index or PDF links retrieved |
| homepage (raw) | https://www.gaappeals.gov/ | 405 | 2,511 | `a9fd810a66fe6380b91c96c40622826350196f1921d0723c9a432718010477a9` | Same WAF challenge |

The site (gaappeals.gov, successor to gaappeals.us) provides an Opinion Search page and Docket/Case Inquiry System. robots.txt allows most paths but disallows /wp-admin/. Lexis was not opened or scraped. No corpus coverage is claimed. Gap: WAF blocks unauthenticated bulk inventory of opinion indexes from this runner; individual opinion PDFs remain available via the court's eFast or public docket after human verification or other access.

Fetch date: 2026-10-29. Citation: Court of Appeals of Georgia opinion search index (access point only). Source URL: https://www.gaappeals.gov/opinion-search/ .
