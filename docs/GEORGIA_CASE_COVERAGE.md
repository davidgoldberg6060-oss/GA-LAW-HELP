Last production check: 2026-10-16 17:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,194 | `992c501462199edbb4b3f800c4a07fed6c40d44ff41a56d71514a0c3da0911c4` | 3 PDF anchors (Supreme Court Rules eff. July 2 2026, chart, quick-reference); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The rules index names 3 PDF links. None of those PDFs were fetched. Prior 2026-10-13 check of the same URL had 1,592,694 bytes and a different SHA-256. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-rules.md`.

