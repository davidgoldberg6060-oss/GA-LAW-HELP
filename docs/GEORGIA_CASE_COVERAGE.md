Last production check: 2026-10-14 00:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only attempt on the Court of Appeals of Georgia rules index. Both the index and robots.txt returned an AWS WAF captcha page; no rule pages or rule text were obtained; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `98e77c7014241b88af42599b58788e190b410d1cdde9097aad0fae3d662c4b8d` | AWS WAF captcha; no index content |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `bfdc473a6d84b319112848ce74606eecd96985d980c87a949401a1e14eb7b5d1` | Same captcha page |

No rule-page links or rule text were retrieved. The prior 2026-10-13 pass also noted Court of Appeals rules pages were not fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-14-coa-rules-index.md`.

Last production check: 2026-10-13 16:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other-court-rules and rules indexes. Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,719 | `08411b3a60c162ce26230c41261c53990ba8068380065a201bc7d78e6dc04c32` | Index labels only |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,694 | `c60a61aeee1fe49912bbde1eb67feb622d213964609bbda77112d840e4dc4e6b` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

The other-court-rules index names 7 Uniform/other rule PDF links (Superior 2026-04-09, State 2024-01-18, Juvenile 2026-09-03, Probate 2023-06-01, Magistrate 2023-04-01, Municipal 2024-12-12, Statewide Business 2026-06-11). The rules index names the Supreme Court Rules PDF effective July 2, 2026 plus a chart and quick-reference PDF. robots.txt disallows `/wp-content/uploads/`, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Court of Appeals rules pages were not fetched in this pass. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-13-court-rules-indexes.md`.
