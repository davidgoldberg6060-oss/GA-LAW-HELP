# Court of Appeals rules pages checkpoint (2026-10-19)

DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals rules entry page and robots.txt.

Both returned the AWS WAF captcha (HTTP 405). No rule text was stored. Not current-law verification. Lexis was not opened.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules-1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `01ebf37f703be5f1535981872d5a0accfd5e15b1af8aee47e393748364da0564` | WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `38ba188d1db4bece07f7bafd7221dee593a97ae631aad66ee84031099d0290b5` | Same WAF captcha page |

These counts are not persisted coverage. Prior checkpoints noted the same WAF behavior on opinion-search and rules indexes.
