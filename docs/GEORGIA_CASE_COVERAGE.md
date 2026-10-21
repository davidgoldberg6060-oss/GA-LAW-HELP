Last production check: 2026-10-21 01:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,194 | `0376b559c981b2a1b591a5c24e54bcd4dc458e62b27caed69c3f6e5aadb3365c` | 3 PDF anchors (SupremeCourtRules_eff-July-2-2026.pdf, CHART-WEB-POSTING-July-2-2026.pdf, QUICK-REFERENCE-RULES.pdf); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The index names the Supreme Court Rules PDF effective July 2, 2026 plus a chart and quick-reference PDF. None were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-21-supreme-rules.md`. Prior 2026-10-13 rules index hash differed.

Last production check: 2026-10-20 18:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other codes and rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other codes and rules index | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,597,306 | `5d917fe128bb058f05f79a1a01dbdbe072b2dc99de5855705e23dbc1ce5c205b` | 28 PDF anchors (27 unique), all under /wp-content/uploads/; 105 unique hrefs total; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The index names 27 unique code/rule/order PDF links (Code of Judicial Conduct, Unified Appeal Procedure, Uniform Misdemeanor Citation, Uniform Transfer Rule, Jury Composition Rule, Rules for Legal Interpreting, and others). None were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-20-supreme-other-codes-rules.md`.

Last production check: 2026-10-19 20:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2025 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2025 opinions index | https://www.gasupreme.us/2025-opinions/ | 200 | 1,624,761 | `603b124f7c3ff8c5fe1541a778bf33b3d294cd36863f50d8d356af2b014d1beb` | ~274 .pdf mentions; 288 /wp-content/uploads/ references; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The 2025 index names opinion and summary PDF links under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-19-supreme-2025.md`.

[Full prior ledger restored; prior content continues from the 2026-10-19 forthcoming opinions checkpoint onward as in the previous full file.]