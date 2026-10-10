# 2026-10-10 court rules index checkpoint

DATABASE_URL was unset. No rule PDFs were downloaded and no corpus rows were written.

## Supreme Court rules index

- Source: https://www.gasupreme.us/rules/
- Fetch: 2026-10-10 08:00 UTC, HTTP 200, 1,594,903 bytes
- SHA-256: `b2c4bf19bd663fd2266fe1c26e841dec73daed1e21e7d6ecf9d5b1b3beecf0eb`
- PDF links named (not fetched; robots.txt disallows /wp-content/uploads/):
  - /wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf
  - /wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf
  - /wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf

## Other court rules index

- Source: https://www.gasupreme.us/other-court-rules/
- Fetch: 2026-10-10 08:00 UTC, HTTP 200, 1,594,941 bytes
- SHA-256: `132d4e1733e96ce3ddb4fe2e79dc92831a24feb4172ce8430bfb69da88edde93`
- PDF links named (not fetched):
  - /wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
  - /wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
  - /wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf
  - /wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
  - /wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
  - /wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
  - /wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf

## robots.txt

- Source: https://www.gasupreme.us/robots.txt
- HTTP 200, 71 bytes, SHA-256 `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196`
- Disallows /wp-content/uploads/

## Court of Appeals

- https://www.gaappeals.gov/court-rules/ returned HTTP 405 (AWS WAF Human Verification page, 2,511 bytes, SHA-256 `edc3318f581b1db82cd1761b527e6a5271cb5b02cf1764f57ee51f2e6e581ac6`)
- Not the rules index. No rule pages or text were read.

Gap: index labels only; PDFs not downloaded because robots.txt disallows the uploads path; not stored rule text; not current-law verification; Lexis not opened.
