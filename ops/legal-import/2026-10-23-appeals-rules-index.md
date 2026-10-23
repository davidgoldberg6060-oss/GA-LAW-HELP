# 2026-10-23 Court of Appeals of Georgia rules index checkpoint

DATABASE_URL was unset. Discover-only fetch of https://www.gaappeals.gov/rules/ and robots.txt. Both returned AWS WAF captcha pages; rule text was not retrieved; not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `00494935a23b290708f68714dc3b2c1b04a8fdcedb120cde240995c86563dbf1` | AWS WAF captcha; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `c9fadd5cc6acc9b489081ae69895ca2d9a793cc74981776badcfd38c604257db` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge for both. No rule PDF anchors or text were named. Lexis was not opened. These counts are not persisted coverage. Gap continues for Court of Appeals rules. No corpus rows written.
