# Court rules indexes checkpoint (2026-10-16)

Fetch date: 2026-10-16 09:01 UTC. DATABASE_URL is unset. No rule PDFs or HTML rule text were downloaded or stored. No authority rows were written. This is not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,194 | `942d14fe8d1bc1a602138148ca490a4d6bb07afffae60522adf49403cbe40b56` | Index labels only; prior 2026-10-13 hash differed (1,592,694 bytes) |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,586,232 | `869fff748b5e96fcbbf5db9bcbefa92fc2a6a048ed0267764211818f14bcb32b` | Index labels only; prior 2026-10-13 hash differed (1,592,719 bytes) |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |
| CoA rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `0aa265838c365b8a3f2775b00b3b8d762c05989aee29d0e8eb1904125a332318` | AWS WAF captcha; not a rules index |

The Supreme Court rules index names three PDF links: SupremeCourtRules_eff-July-2-2026.pdf, CHART-WEB-POSTING-July-2-2026.pdf, and QUICK-REFERENCE-RULES.pdf. The other-court-rules index names seven Uniform/other rule PDF links (Superior 2026-04-09, State 2024-01-18, Juvenile 2026-09-03, Probate 2023-06-01, Magistrate 2023-04-01, Municipal 2024-12-12, Statewide Business 2026-06-11). robots.txt disallows `/wp-content/uploads/`, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Court of Appeals rules index returned the Human Verification challenge on raw fetch. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the index pages only. Rule PDFs remain unfetched because of robots.txt. CoA rules pages remain blocked by WAF on raw fetch. Missing DATABASE_URL means no corpus rows can be written. Currency is unknown pending later official comparison.
