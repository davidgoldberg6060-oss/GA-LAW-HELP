# Court rules indexes — discover-only checkpoint

Fetch date: 2026-10-13 (UTC). DATABASE_URL was unset, so no PDF files were downloaded and no corpus rows were written.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,719 | `08411b3a60c162ce26230c41261c53990ba8068380065a201bc7d78e6dc04c32` | Index labels only |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,694 | `c60a61aeee1fe49912bbde1eb67feb622d213964609bbda77112d840e4dc4e6b` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDFs were fetched. Filenames are index labels, not effective dates, not stored rule text, and not current-law verification. Lexis was not opened. These counts are not persisted coverage.

## Uniform / other court rules PDFs named (not downloaded)

| File | URL |
| --- | --- |
| UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf | https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf |
| UNIFORM-STATE-COURT-RULES-2024_01_18.pdf | https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf |
| UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf | https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf |
| UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf | https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf |
| UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf | https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf |
| UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf | https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf |
| State-wide-Business-Court-Rules-2026_06_11.pdf | https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf |

## Supreme Court rules PDFs named (not downloaded)

| File | URL |
| --- | --- |
| SupremeCourtRules_eff-July-2-2026.pdf | https://www.gasupreme.us/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf |
| CHART-WEB-POSTING-July-2-2026.pdf | https://www.gasupreme.us/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf |
| QUICK-REFERENCE-RULES.pdf | https://www.gasupreme.us/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf |

Gap notes: index inventory only. Companion Court of Appeals rules are linked to www.gaappeals.gov (prior WAF block on opinion search; rules pages not fetched here). No corpus rows written. Missing DATABASE_URL means no authority rows can be written.
