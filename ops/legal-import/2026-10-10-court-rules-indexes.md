# Georgia court rules indexes — discover-only checkpoint

Fetch date: 2026-10-10 (UTC). DATABASE_URL was unset, so no PDF files were downloaded and no corpus rows were written.

Sources:
- https://www.gasupreme.us/other-court-rules/
- https://www.gasupreme.us/other-codes-rules/
- https://www.gasupreme.us/robots.txt

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `2baf5dbeccd1b5621cbbeeabc222c89a13e94d7cae057bb12db98a5cb4da3a61` | Index labels only; PDFs not fetched |
| other-codes-rules index | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,606,015 | `28dacea222c726283e9f14a3d4c7c3d8cbcbb92fa4a68a9d580a160689dca14f` | Index labels only; PDFs not fetched |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

robots.txt disallows `/wp-content/uploads/`, so every PDF linked from these indexes is blocked for automatic fetch. None were downloaded. Filenames are index labels only, not effective dates and not stored rule text. Court of Appeals rules are linked as HTML pages on gaappeals.gov (not inventoried here). Lexis was not opened.

These are index checkpoints, not stored court-rule text, not proof of current law, and not coverage. A missing DATABASE_URL means no authority rows can be written.

## other-court-rules PDF links (not downloaded)

- /wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
- /wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
- /wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
- /wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- /wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
- /wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf
- /wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf

## other-codes-rules PDF links (not downloaded; 27 unique)

Examples (full list in page source; all under /wp-content/uploads/):
- Code-of-Judicial-Conduct-2024_02_01.pdf
- JQC-RULES-2023_02_03.pdf
- RulesForLegalInterpreting_updatedMarch2025.pdf
- Statewide-Min-Standards-Rules-final.pdf
- UNIFIED_APPEAL-06_06_18.pdf
- Uniform_Misdemeanor_Citation_Rules_FINAL_REVISED_07-01-2019.pdf
- and related amendment/order PDFs.

Gap notes: index inventory only. PDFs contain the official rule texts and orders but were not fetched because of robots.txt. No corpus rows written. Currency remains unknown.
