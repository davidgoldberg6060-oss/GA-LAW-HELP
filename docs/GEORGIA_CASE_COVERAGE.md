Last production check: 2026-10-20 11:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2024 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2024 opinions index | https://www.gasupreme.us/2024-opinions/ | 200 | 1,623,709 | `2645b0747919964ef5d66ce58279e24276d70b628619a217b82885075845c3d3` | 262 PDF anchors (252 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The 2024 index names 262 PDF link anchors (252 unique URLs) under /wp-content/uploads/. Sample docket labels include S22A0605, S22A1326, S22G1146. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-20-supreme-2024.md`.

Last production check: 2026-10-19 20:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2025 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2025 opinions index | https://www.gasupreme.us/2025-opinions/ | 200 | 1,624,761 | `603b124f7c3ff8c5fe1541a778bf33b3d294cd36863f50d8d356af2b014d1beb` | ~274 .pdf mentions; 288 /wp-content/uploads/ references; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The 2025 index names opinion and summary PDF links under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-19-supreme-2025.md`.
