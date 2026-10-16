Last production check: 2026-10-16 16:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of Court of Appeals rules pages (rules-1-8, /rules/, homepage) and robots.txt. All returned the AWS WAF captcha (HTTP 405). Page bytes were hashed; no rule text or PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules-1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `6c3f5ea029797a7d7562b1ab1756e502b41d10e969276d496cf7360de1f3e090` | WAF captcha; not rule text |
| /rules/ | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `093b352a891acb836db56f3674a3064f078c310cc6979be4606458398ed9d943` | WAF captcha; not an index |
| homepage | https://www.gaappeals.gov/ | 405 | 2,511 | `c7e0e2807eb44504343ecf4c9e983dcc2f2f708650e0d062f505f477d287226f` | WAF captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `e489a32ea4d5e6317e9d50f0cf4fde07e0720783e9b930baea2e27152214b5c2` | Same WAF captcha page |

Raw fetches returned the Human Verification challenge. No rule PDF anchors were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-coa-rules-waf.md`. Opinion-search remains blocked the same way.

PLACEHOLDER_HISTORY