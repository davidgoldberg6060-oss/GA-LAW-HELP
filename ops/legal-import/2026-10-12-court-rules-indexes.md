# Court rules indexes checkpoint — 2026-10-12

DATABASE_URL was unset. No corpus rows were written. No coverage is claimed.

Discover-only read of the Supreme Court of Georgia rules index pages. Index HTML was hashed. Linked PDFs live under `/wp-content/uploads/` which `robots.txt` disallows, so none were downloaded. Not stored rule text and not current-law verification. Lexis was not opened.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| Supreme Court rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `67c53f5118b4456a0c011c784ab9a2ea98d02b328372910e818e6ce56ff43291` | Index labels only |
| Other court rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `3d8c2415d1b3e9fa7b36dc04c4ace934a13ba83f845704c89e4b5748f4174299` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

Named PDF labels (not fetched; blocked by robots):

- Supreme Court Rules: `/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf`
- Quick Reference: `/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf`
- Chart: `/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf`
- Uniform Superior Court Rules: `/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf`
- Uniform State Court Rules: `/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf`
- Uniform Juvenile Court Rules: `/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf`
- Uniform Probate Court Rules: `/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf`
- Uniform Magistrate Court Rules: `/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf`
- Uniform Municipal Court Rules: `/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf`
- Statewide Business Court Rules: `/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf`

Court of Appeals rules index (`https://www.gaappeals.gov/court-rules/`) and its robots.txt returned HTTP 405 (WAF/captcha shell, same as prior appeals opinion-search checks). Not fetched. Gap: CoA rules HTML not reachable under automated polite fetch this session.

Importer note: `import_court_rules.py` already treats these gasupreme.us PDFs as `blocked_by_robots` and supports manual `--pdf-dir` for operator-provided files. This checkpoint records the current index labels and hashes only.