# Supreme Court 2026 opinions index checkpoint (2026-10-29)

Fetch date: 2026-10-29 10:02 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,634,295 | `dad7eb72cd9dc72db225b0239918962679377f7cd456339baaae42dbd8a018cf` | Index labels only; 294 PDF anchors (285 unique docket-like tokens) |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

Raw fetch of the annual index succeeded (HTTP 200). 294 PDF link anchors were named under `/wp-content/uploads/`. robots.txt disallows that path, so none of the PDF files were fetched. Prior 2026-10-16 checkpoint recorded 1,625,440 bytes / 283 PDF anchors; the index has grown. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the 2026 index labels only. Opinion PDFs remain unfetched. Missing DATABASE_URL means no corpus rows can be written. Currency of listed opinions is unknown; the index is not a verification of binding current law.
