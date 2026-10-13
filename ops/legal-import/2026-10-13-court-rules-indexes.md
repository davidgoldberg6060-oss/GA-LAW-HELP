# Court rules indexes inventory — 2026-10-13

Discover-only. DATABASE_URL was unset in this environment, so no corpus rows were written and no coverage is claimed. Lexis was not opened. PDFs under `/wp-content/uploads/` were not downloaded because `robots.txt` disallows that path.

## Supreme Court other-court-rules

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,719 | `f9d3b8d2ba2540906985bd01c763e5748006c5f684dd6984f9495c9f786d7748` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

Named PDF links (none downloaded; filenames are not effective dates and not stored rule text):

- UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf — https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
- UNIFORM-STATE-COURT-RULES-2024_01_18.pdf — https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
- UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf — https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf
- UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf — https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
- UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf — https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
- UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf — https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- State-wide-Business-Court-Rules-2026_06_11.pdf — https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf

Gap: robots.txt blocks automatic fetch of the official PDFs. An operator may download them by hand and pass `--pdf-dir` to the court-rules importer.

## Supreme Court rules

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| Supreme Court rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,694 | `c8be4f87eba017ac0fa2922693ab12ddccf8953ea4f2c678d1056476a74eb79b` | Index labels only |

Named PDF links (none downloaded):

- SupremeCourtRules_eff-July-2-2026.pdf
- QUICK-REFERENCE-RULES.pdf
- CHART-WEB-POSTING-July-2-2026.pdf

Same robots.txt disallow applies.

## Court of Appeals court-rules

Direct curl to https://www.gaappeals.gov/court-rules/ returned HTTP 405 (AWS WAF captcha page, 2,511 bytes, SHA-256 `cf84034591b589b34238bf5ea479dd252e9a2dbf69601504cb73acf40562fc25`). Not the court index. A browser-rendered view of the same URL listed rule-page links (Rules 1-8, 11-15, etc.) but those pages were not fetched and are not stored. Prior WAF blocks on the opinion-search page remain.

## other-codes-rules

https://www.gasupreme.us/other-codes-rules/ returned HTTP 403. No inventory.

These counts are not persisted coverage. No statute or case text was invented.
