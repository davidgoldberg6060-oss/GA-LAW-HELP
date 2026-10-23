# 2026-10-23 Court of Appeals rules index checkpoint

DATABASE_URL was unset. Discover-only raw fetch of the Court of Appeals rules index (https://www.gaappeals.gov/rules/) and robots.txt.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `f0c75beaadfb037f717393aa7cfaa6fe268ccbe2e696487c752e0a7df52f8445` | AWS WAF captcha; not rules text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `49a20f08bdc9f413f8a6bbfd9f9ed078dc4ee7646e421957d6190b19b27553b3` | Same WAF captcha page |

Raw fetch returned the Human Verification / AWS WAF challenge for both. No rule text or PDF anchors were retrieved or stored. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
