# 2026-10-23 Supreme Court of Georgia rules index checkpoint

DATABASE_URL was unset. Discover-only fetch of https://www.gasupreme.us/rules/. Index bytes were hashed; PDF targets under /wp-content/uploads/ were not downloaded because robots.txt disallows that path. Not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `4ffe25395619943f6f19c943932272c97907748dc7e9a389964676693a308729` | 3 PDF anchors under /wp-content/uploads/ (Supreme Court Rules eff. July 2, 2026; chart; quick-reference); robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The rules index names the Supreme Court Rules PDF effective July 2, 2026, a chart, and a quick-reference PDF. None were fetched. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
