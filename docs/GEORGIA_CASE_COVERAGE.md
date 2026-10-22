Last production check: 2026-10-22 08:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2024 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2024 opinions index | https://www.gasupreme.us/2024-opinions/ | 200 | 1,623,746 | `67e37bd8dcefdc51197dd71d4f521fce9e5913f69a3673b77ac28585695bdf59` | 262 PDF anchors (252 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The 2024 index names opinion and summary PDF links under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-supreme-2024.md`.

Last production check: 2026-10-22 06:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:
