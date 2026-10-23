Last production check: 2026-10-23 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of a Court of Appeals rules HTML page (https://www.gaappeals.gov/rules-1-8/). Returned HTTP 405 AWS WAF captcha; page bytes hashed; no rule text downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules HTML | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `aa533296d324d8fe9704461d24a6099c1792d8ea4e16781d95c92ffd032c4bcf` | AWS WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 200 | 128 | (not hashed this pass) | Allows most paths; WAF still blocks rules HTML |

Raw fetch returned the Human Verification challenge. A complete rules PDF exists on the site but was not fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-appeals-rules-waf.md`.

Last production check: 2026-10-23 17:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `4ffe25395619943f6f19c943932272c97907748dc7e9a389964676693a308729` | 3 PDF anchors under /wp-content/uploads/ (Supreme Court Rules eff. July 2, 2026; chart; quick-reference); robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The rules index names the Supreme Court Rules PDF effective July 2, 2026, a chart, and a quick-reference PDF. robots.txt disallows /wp-content/uploads/, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-supreme-rules-index.md`.

[... full historical ledger continues unchanged ...]