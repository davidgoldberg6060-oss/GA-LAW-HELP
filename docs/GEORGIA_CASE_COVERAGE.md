Last production check: 2026-10-21 08:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,194 | `f74bb525d914f57ac99de73c891f15477fa636c8fd35d03d3bcd9558befb9f53` | 3 unique PDF anchors under /wp-content/uploads/; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The index names three PDF links: current Supreme Court Rules effective July 2, 2026; Rule Changes & Amendment History Chart – 2026 Updates; and Quick Reference. All under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-21-supreme-rules-index.md`.

