# 2026-10-10 Court rules index checkpoints

DATABASE_URL was unset. No rule PDF was downloaded and no corpus rows were written.

Discover-only hashed the official court-rules index pages and robots.txt (page bytes and PDF link labels only; rule PDFs not downloaded; not stored rule text and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| other-court-rules | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `9c7e49665988f809fce1ef2615b4c43e693532134930b5925fd47f838fd05bfd` | 7 |
| supreme rules | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `bd04ea9a7ac229bfd9f61223d6291038626f409de0f493fdd86a4fa720532562` | 3 |
| other-codes-rules | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,606,015 | `270e1fd51384d1c328e780b977844cc9ec3d9096a03372307d4361c664b4aaef` | 27 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDFs were fetched. Lexis was not opened. These counts are not persisted coverage.

## other-court-rules PDF labels (not downloaded)

| File | URL | Gap |
| --- | --- | --- |
| UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf | https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf | Index label only; PDF not downloaded; filename is not an effective date and not stored rule text |
| UNIFORM-STATE-COURT-RULES-2024_01_18.pdf | https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf | Index label only; PDF not downloaded; filename is not an effective date and not stored rule text |
| UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf | https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf | Index label only; PDF not downloaded; filename is not an effective date and not stored rule text |
| UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf | https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf | Index label only; PDF not downloaded; filename is not an effective date and not stored rule text |
| UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf | https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf | Index label only; PDF not downloaded; filename is not an effective date and not stored rule text |
| UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf | https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf | Index label only; PDF not downloaded; filename is not an effective date and not stored rule text |
| State-wide-Business-Court-Rules-2026_06_11.pdf | https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf | Index label only; PDF not downloaded; filename is not an effective date and not stored rule text |

## supreme rules PDF labels (not downloaded)

| File | URL | Gap |
| --- | --- | --- |
| SupremeCourtRules_eff-July-2-2026.pdf | https://www.gasupreme.us/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf | Index label only; PDF not downloaded; label claims effective July 2, 2026 but not verified and not stored rule text |
| CHART-WEB-POSTING-July-2-2026.pdf | https://www.gasupreme.us/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf | Index label only; PDF not downloaded; amendment chart, not stored rule text |
| QUICK-REFERENCE-RULES.pdf | https://www.gasupreme.us/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf | Index label only; PDF not downloaded; summary, not stored rule text |

## other-codes-rules PDF labels (not downloaded)

27 PDF links named on the index. Full list recorded in this checkpoint. None downloaded. Filenames are not effective dates and not stored rule text. Examples include Code of Judicial Conduct, Uniform Appeal Procedure, Uniform Misdemeanor Citation rules, and Judicial Qualifications Commission rules. Court of Appeals HTML rule pages were not fetched (prior WAF 405). Lexis was not opened.
