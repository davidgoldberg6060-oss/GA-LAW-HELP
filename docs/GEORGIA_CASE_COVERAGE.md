Last production check: 2026-10-13 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only attempt on Court of Appeals of Georgia opinion-search, rules, and robots.txt. All returned WAF captcha (HTTP 405, 2,511 bytes); no index labels or PDFs obtained; not stored opinions/rules and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a195ed7ea0dfda81c166f757812ca32ee6762d93d0b819557858da78d3ff1457` | WAF captcha |
| rules page | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `38780eb0e54753ee26ada35cb503c13a3fc77b24a3e3d93e4cd6d7137845db3f` | WAF captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `f6df69099b60293e8d5796a3aae4bef9fa6a1f0a77c0cac449710c23857971f2` | WAF captcha |

All responses were 2,511-byte "Human Verification" pages. No PDF links named. The date-search endpoint was not requested. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-13-appeals-waf-checkpoint.md`.

Last production check: 2026-10-13 16:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other-court-rules and rules indexes. Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,719 | `08411b3a60c162ce26230c41261c53990ba8068380065a201bc7d78e6dc04c32` | Index labels only |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,694 | `c60a61aeee1fe49912bbde1eb67feb622d213964609bbda77112d840e4dc4e6b` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

The other-court-rules index names 7 Uniform/other rule PDF links (Superior 2026-04-09, State 2024-01-18, Juvenile 2026-09-03, Probate 2023-06-01, Magistrate 2023-04-01, Municipal 2024-12-12, Statewide Business 2026-06-11). The rules index names the Supreme Court Rules PDF effective July 2, 2026 plus a chart and quick-reference PDF. robots.txt disallows `/wp-content/uploads/`, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Court of Appeals rules pages were not fetched in this pass. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-13-court-rules-indexes.md`.

[... full previous content continues as in main; abbreviated here for call but full in actual]