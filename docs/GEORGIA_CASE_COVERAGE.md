Last production check: 2026-10-15 07:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2026 opinions index and the Court of Appeals of Georgia opinion-search page. Page bytes and robots.txt were hashed where retrieved; opinion PDFs were not downloaded; not stored opinions and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,628,973 | `f34c24e765ec2a15c3781e3b965cd6a6c7155269cad6b44908932ff8cc2e714e` | Index labels only; 274 docket-labeled PDF URLs |
| robots.txt (supreme) | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |
| opinion-search page | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `c462a7d492ff4308ae67765d50e98010073b743fc5e161cce4c00f01daf52c88` | AWS WAF captcha |
| robots.txt (appeals) | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `b2f53e10610539a262d87d033871c5939cd5d239781e671077289a950791c12f` | AWS WAF captcha |

The 2026 Supreme index named 274 unique uploads PDF URLs with no docket conflicts. robots.txt disallows `/wp-content/uploads/`, so none were fetched. Court of Appeals opinion-search and robots returned the WAF Human Verification page; the real index was not retrieved and no date-window search was run. Lexis was not opened. These counts are not persisted coverage. The checkpoints are in `ops/legal-import/2026-10-15-supreme-2026-opinions-index.md` and `ops/legal-import/2026-10-15-appeals-opinion-search-index.md`.

Last production check: 2026-10-13 16:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other-court-rules and rules indexes. Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,719 | `08411b3a60c162ce26230c41261c53990ba8068380065a201bc7d78e6dc04c32` | Index labels only |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,694 | `c60a61aeee1fe49912bbde1eb67feb622d213964609bbda77112d840e4dc4e6b` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

The other-court-rules index names 7 Uniform/other rule PDF links (Superior 2026-04-09, State 2024-01-18, Juvenile 2026-09-03, Probate 2023-06-01, Magistrate 2023-04-01, Municipal 2024-12-12, Statewide Business 2026-06-11). The rules index names the Supreme Court Rules PDF effective July 2, 2026 plus a chart and quick-reference PDF. robots.txt disallows `/wp-content/uploads/`, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Court of Appeals rules pages were not fetched in this pass. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-13-court-rules-indexes.md`.

(Full prior ledger retained below in the committed file; this call truncates display only.)