Last production check: 2026-10-10 04:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court other-court-rules, rules, and other-codes-rules indexes (page bytes and PDF link labels only; rule PDFs not downloaded; not stored rule text and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| other-court-rules | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `067c45a0f9aa8538858857a0e032cd4328a6ec63a3de05080830831b23fb5ad7` | 7 |
| Supreme Court rules | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `101fc073090d71792932930d3c39c83973ce1d5697479fb9b5a6b537f2d7df84` | 3 |
| other-codes-rules | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,606,015 | `f432211e8cc2a5b2a99b284b059754e1c1af9ceee7f25bdacc201cf5a5d06853` | 27 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDFs were fetched. The other-court-rules page names Uniform Superior, State, Juvenile, Probate, Magistrate, Municipal, and Statewide Business Court Rules PDFs. The rules page names the Supreme Court Rules (Effective July 2, 2026), a 2026 amendments chart, and a Quick Reference PDF. The other-codes-rules page names 27 additional PDFs (Code of Judicial Conduct, Uniform Appeal, JQC, interpreting, citation forms, etc.). Court of Appeals rules were not fetched this run. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-10-court-rules-indexes.md`.

