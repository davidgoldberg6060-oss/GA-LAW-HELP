Last production check: 2026-10-23 19:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2023 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2023 opinions index | https://www.gasupreme.us/2023-opinions/ | 200 | 1,620,936 | `ca938be4bde6c4463cba9a733c0accf4b5bc3ebccf817f6fa8de6657e2f29065` | ~244 .pdf mentions; all under /wp-content/uploads/; robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The 2023 index names opinion and summary PDF links under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-supreme-2023.md`.

