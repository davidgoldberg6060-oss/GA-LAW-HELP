Last production check: 2026-10-18 18:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2025 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2025 opinions index | https://www.gasupreme.us/2025-opinions/ | 200 | 1,624,761 | `fdccff95074407c91b9b6797015517852acd82496a336b91da449e172ddc90ae` | 274 PDF anchors (271 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

Raw fetch returned the year index page. 274 PDF link anchors named (271 unique). No opinion PDFs were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-18-supreme-2025.md`.

