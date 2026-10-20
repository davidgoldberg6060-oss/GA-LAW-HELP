Last production check: 2026-10-20 07:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index, other-court-rules index, and robots.txt. Page bytes were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,194 | `8992a09e6a7ea074f2b1c7f40d6a1f84363c27a207a1d0372356288dec187b3f` | 3 PDF anchors under /wp-content/uploads/; robots disallow that path |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,586,219 | `53371f0cebbf2e1c2b518e81f306ea5268d61dbdff9eb94261c27b5404f9b208` | 7 Uniform/other rule PDF anchors; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The rules index names the Supreme Court Rules PDF effective July 2, 2026, a 2026 chart, and a quick-reference PDF. The other-court-rules index names Uniform Superior (2026-04-09), State (2024-01-18), Juvenile (2026-09-03 ADA), Probate (2023-06-01), Magistrate (2023-04-01), Municipal (2024-12-12), and Statewide Business (2026-06-11). robots.txt disallows `/wp-content/uploads/`, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-20-court-rules-indexes.md`.

PLACEHOLDER_REMAINING_HISTORY