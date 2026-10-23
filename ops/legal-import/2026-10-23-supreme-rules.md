# 2026-10-23 Supreme Court rules index checkpoint

DATABASE_URL was unset. Discover-only fetch of the Supreme Court of Georgia rules index (https://www.gasupreme.us/rules/) and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no PDFs were downloaded; not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `c71bfc00556d142cd1b61c758e719b6998d02353e4593ab0ec6d4344f0eacadf` | 3 PDF anchors (3 unique), all under /wp-content/uploads/; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The rules index names the Supreme Court Rules PDF and related reference PDFs. None were fetched. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
