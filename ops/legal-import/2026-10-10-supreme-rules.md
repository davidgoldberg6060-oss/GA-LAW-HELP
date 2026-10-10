# 2026-10-10 Supreme Court of Georgia rules index checkpoint

DATABASE_URL was unset. No rule PDF was downloaded and no corpus rows were written.

- Source: https://www.gasupreme.us/rules/
- HTTP 200, 1,594,916 bytes, SHA-256 `dc77a51ff8469537fb0976686eead78fda144b2af4803ad8b413572a644f2cf4`
- robots.txt: HTTP 200, 71 bytes, SHA-256 `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` (disallows `/wp-content/uploads/`)
- Former-rules page: https://www.gasupreme.us/rules/former-rules/ HTTP 200, 1,707,003 bytes, SHA-256 `5c5e46c5318befef477d9b582941148d1d14737b14f04e9eb5681bfcf3e3d2b0`
- Gap: index labels only; PDFs not downloaded because robots.txt disallows uploads; not stored rule text; effective-date labels on the index are not current-law verification; Lexis not opened

| Label on index | PDF URL | Downloaded |
| --- | --- | --- |
| Rules of the Supreme Court (Effective July 2, 2026) | https://www.gasupreme.us/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf | no |
| Rule Changes & Amendment History (Chart – 2026 Updates) | https://www.gasupreme.us/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf | no |
| Quick Reference | https://www.gasupreme.us/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf | no |

The former-rules page names the current PDF above and a Certificate of Timeliness template. Its HTML body contains numbered rule headings (Rule 1. OFFICE HOURS onward) and states that the rules were amended on January 1, 2024 and that the current Rules page should be used. That HTML was not parsed into rule text and was not stored. These counts are not persisted coverage.
