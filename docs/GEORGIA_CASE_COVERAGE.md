Last production check: 2026-10-23 13:03 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index (https://www.gasupreme.us/rules/). Index bytes were hashed; PDF anchors counted; robots.txt disallows /wp-content/uploads/ so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `7108e08ae79553641ea584d1beafa882841cbaa2a1f718213884923cb7a7d45e` | 3 unique PDF anchors under /wp-content/uploads/ (SupremeCourtRules_eff-July-2-2026.pdf, CHART-WEB-POSTING-July-2-2026.pdf, QUICK-REFERENCE-RULES.pdf); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The index names the current Supreme Court Rules PDF effective July 2, 2026, a chart, and a quick-reference PDF. None were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-supreme-rules-index.md`. Prior 2026-10-13 checkpoint of the same index recorded 1,592,694 bytes.

Last production check: 2026-10-23 09:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Judicial Council / Administrative Office of the Courts Supreme Court and related rules index (https://georgiacourts.gov/georgia-supreme-court-rules/). Index bytes were hashed; PDF anchors counted; gasupreme.us robots.txt disallows /wp-content/uploads/ so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `8fc27ecebaa34124a3ed2169192c825400992959bbb8ea00653afd47c2287cb3` | 28 PDF anchors, all under www.gasupreme.us/wp-content/uploads/; robots on gasupreme.us disallow /wp-content/uploads/ |

The index names 28 unique PDF links (Supreme Court Rules eff. 1.1.24, Uniform Superior/State/Juvenile/Probate/Magistrate/Municipal Court Rules of various dates, Statewide Business Court, Unified Appeal, Uniform Misdemeanor Citation, Transfer Rule, Interpreting, Jury Composition, JQC Rules, and others). None were fetched. More recent versions exist on the gasupreme.us other-court-rules index. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-georgiacourts-rules-index.md`.

