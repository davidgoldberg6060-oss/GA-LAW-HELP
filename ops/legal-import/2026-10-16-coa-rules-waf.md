# 2026-10-16 Court of Appeals rules indexes (WAF captcha)

DATABASE_URL was unset, so no corpus rows were written and no authority versions were stored.

Discover-only raw fetches of Court of Appeals rules pages and robots.txt. All returned the AWS WAF Human Verification captcha (HTTP 405). Page bytes were hashed; no rule PDFs or HTML rule text were downloaded. Not stored rule text and not current-law verification. Lexis was not opened.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules-1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `6c3f5ea029797a7d7562b1ab1756e502b41d10e969276d496cf7360de1f3e090` | WAF captcha; not rule text |
| /rules/ | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `093b352a891acb836db56f3674a3064f078c310cc6979be4606458398ed9d943` | WAF captcha; not an index |
| homepage | https://www.gaappeals.gov/ | 405 | 2,511 | `c7e0e2807eb44504343ecf4c9e983dcc2f2f708650e0d062f505f477d287226f` | WAF captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `e489a32ea4d5e6317e9d50f0cf4fde07e0720783e9b930baea2e27152214b5c2` | Same WAF captcha page |

Captcha pages are dynamic; later fetches produce different hashes of the same challenge template. No docket or rule PDF anchors were named. These counts are not persisted coverage. Opinion-search remains blocked the same way (see 2026-10-15 checkpoint).
