Last production check: 2026-10-22 13:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `b0ebe12f73101bbe2fe49823f5eaff4c4cdad9bb57f5ba133df082337db88ad5` | 3 PDF anchors, all under /wp-content/uploads/; prior 2026-10-13 hash differed |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The rules index names the Supreme Court Rules PDF effective July 2, 2026, a chart PDF, and a quick-reference PDF. All point under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-supreme-rules.md`.

