# Discover-only checkpoint: Georgia court rules indexes (2026-10-11)

DATABASE_URL was unset, so no corpus rows were written and no coverage is claimed.

Fetched indexes only. PDF files under `/wp-content/uploads/` were not downloaded (robots.txt disallows that path). These are index labels and official URLs, not stored rule text and not current-law verification. Lexis was not opened.

## Supreme Court of Georgia Rules

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `b61de01934a3687fb6e70a1d44645854a2a7bbb978728c4f05448223b37ff0f6` | Index only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

Named PDF links (none downloaded):

- https://www.gasupreme.us/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf (labeled "Rules of the Supreme Court (Effective July 2, 2026)")
- https://www.gasupreme.us/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf (labeled "Rule Changes & Amendment History (Chart – 2026 Updates)")
- https://www.gasupreme.us/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf (labeled "Quick Reference")

Gap: PDF bytes not fetched; effective-date claim on the index is not verified against document content.

## Other Court Rules (Uniform Rules)

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `b1dc52d87613d6826df7d0e3ddabee749b298cf66743383e37d8ea928d7d8483` | Index only |

Named PDF links (none downloaded; same robots disallow):

- https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
- https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
- https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf
- https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
- https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
- https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf

Gap: Filenames suggest dates but are not verified effective dates; PDFs not stored. Court of Appeals HTML rule pages (www.gaappeals.gov/court-rules/) were not re-fetched in this checkpoint.

Provenance: fetch date 2026-10-11 UTC, user-agent `GA.LAW.HELP-corpus-import/1.0 (+https://github.com/davidgoldberg6060-oss/GA-LAW-HELP)`. No authority rows written.
