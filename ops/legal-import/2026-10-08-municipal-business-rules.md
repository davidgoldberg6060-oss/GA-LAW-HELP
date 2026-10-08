# 2026-10-08 municipal and business court rule index checkpoint

DATABASE_URL was unset. No rule PDFs were downloaded and no authority rows were written. This is an official-index inventory only, not persisted coverage and not current-law verification.

## Other court rules index

- Source: https://www.gasupreme.us/other-court-rules/
- Fetch: 2026-10-08 (later than the 12:01 UTC checkpoint)
- HTTP: 200
- Bytes: 1,592,686
- SHA-256: `7521ebac0df238aaa277224bda88b6c91ad6601736f262f74b857deee2565ed4`
- Earlier same-day page hash `9b6eb00e2a3d9dc49958f7409a7b2544d9ef7297cde643cb423f717e4750504c` had the same byte length. Page hash is not a stable content identity. The PDF filename list below matched the earlier inventory.

PDF links named on the page (uploads path; not fetched):

| Set | Official file name on the index |
| --- | --- |
| superior | `UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf` |
| state | `UNIFORM-STATE-COURT-RULES-2024_01_18.pdf` |
| juvenile | `UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf` |
| probate | `UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf` |
| magistrate | `UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf` |
| municipal | `UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf` |
| business | `State-wide-Business-Court-Rules-2026_06_11.pdf` |

`https://www.gasupreme.us/robots.txt` returned HTTP 200 (71 bytes, SHA-256 `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196`) and disallows `/wp-content/uploads/`. Filename dates are labels on the index, not verified effective dates. Lexis annotations were not scraped.

The importer now registers `municipal` and `business` so `--set all` reports them as `blocked_by_robots` with the official URL instead of omitting them. An operator may still supply a hand-downloaded PDF with `--pdf-dir`. Citation prefixes used only as labels: `Unif. Mun. Ct. R.` and `Statewide Bus. Ct. R.`. No rule text was stored.

## Court of Appeals opinion search

The importer search URL was fetched and not parsed as opinions:

- URL: `https://www.gaappeals.gov/wp-content/themes/benjamin/docket/docketdate/results_all.php?OPstartDate=2026-09-01&OPendDate=2026-09-07&submit=Start+Opinions+Search`
- HTTP: 405
- Body: 2,511 bytes, title Human Verification
- SHA-256: `543716d945c59e328d1af446ee37b55dbb854db78017bcfa0dfbaa419bb35e50`

Related 405 pages the same run (human-verification HTML, not indexes):

| URL | SHA-256 |
| --- | --- |
| https://www.gaappeals.gov/robots.txt | `a11c434498a2e46f8401cb8b8a100f02da03a7f5d474d2cde93d3667d157831e` |
| https://www.gaappeals.gov/ | `aabdb931ea34a3a84f8579a269f6d4f6ab732a38b478b046751f96ef44cfa555` |
| https://www.gaappeals.gov/opinions/ | `7672c4520d7bd6a93f3f35e3d6db7d8b110b74c103c5dc3b2354c05713c9aa4f` |

No opinion PDFs, docket counts, or citations were recorded. CourtListener court metadata for `ga` and `gactapp` returned HTTP 200, but cluster counts require authentication and were not used as coverage.
