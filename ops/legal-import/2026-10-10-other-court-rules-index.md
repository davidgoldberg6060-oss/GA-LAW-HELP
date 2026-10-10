# 2026-10-10 other-court-rules index (discover-only)

DATABASE_URL was unset, so no authority rows were written. Discover-only read of https://www.gasupreme.us/other-court-rules/. Index bytes hashed; PDF files not downloaded; not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `243e6416cb4fad0ab69e02a9a7ab5abaa997fbccc847963bb1706e6f92e0d8fa` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

Named PDF links (none downloaded):

- /wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
- /wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
- /wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf
- /wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
- /wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
- /wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- /wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf

Gap notes: filenames encode approximate dates but are not verified effective dates or current-law status. Court of Appeals rules index (https://www.gaappeals.gov/court-rules/) returned HTTP 405 AWS WAF captcha (2,511 bytes) and was not parsed. Lexis was not opened. These counts are not persisted coverage.
