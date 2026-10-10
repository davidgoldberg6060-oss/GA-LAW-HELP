# 2026-10-10 Court rules indexes checkpoint

DATABASE_URL was unset. No rule PDFs were downloaded and no corpus rows were written.

- Sources:
  - https://www.gasupreme.us/other-court-rules/
  - https://www.gasupreme.us/rules/
  - https://www.gasupreme.us/other-codes-rules/
  - https://www.gasupreme.us/robots.txt
- robots.txt: HTTP 200, 71 bytes, SHA-256 `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196`. Disallows `/wp-content/uploads/`, so every named PDF stayed unfetched.
- Lexis was not opened.
- Gap: index pages and PDF link labels only; not stored rule text; filenames are not effective dates and not current-law verification; not persisted coverage.

## other-court-rules index

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| other-court-rules | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `067c45a0f9aa8538858857a0e032cd4328a6ec63a3de05080830831b23fb5ad7` | 7 |

| Rule set label | PDF URL | Gap |
| --- | --- | --- |
| Uniform Superior Court Rules | https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Uniform State Court Rules | https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Uniform Juvenile Court Rules | https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Uniform Probate Court Rules | https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Uniform Magistrate Court Rules | https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Uniform Municipal Court Rules | https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Statewide Business Court Rules | https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |

Court of Appeals rules link on the page points to https://www.gaappeals.gov/rules-1-8/ (not fetched this run; prior attempts returned WAF 405).

## Supreme Court rules index

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| Supreme Court rules | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `101fc073090d71792932930d3c39c83973ce1d5697479fb9b5a6b537f2d7df84` | 3 |

| Label | PDF URL | Gap |
| --- | --- | --- |
| Rules of the Supreme Court (Effective July 2, 2026) | https://www.gasupreme.us/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Rule Changes & Amendment History (Chart – 2026 Updates) | https://www.gasupreme.us/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |
| Quick Reference | https://www.gasupreme.us/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf | Index label only; PDF not downloaded; robots.txt disallows path; not stored text |

Archived rules link: https://www.gasupreme.us/rules/former-rules (not fetched).

## other-codes-rules index

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| other-codes-rules | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,606,015 | `f432211e8cc2a5b2a99b284b059754e1c1af9ceee7f25bdacc201cf5a5d06853` | 27 |

27 distinct PDF links under /wp-content/uploads/ were named (Code of Judicial Conduct, Uniform Appeal Procedure, Jury Composition Rule, misdemeanor citation forms/rules, JQC rules, legal interpreting, etc.). None were downloaded. Filenames are labels only.

These counts are not persisted coverage.
