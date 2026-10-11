# Georgia court rules indexes — discover-only checkpoint

Fetch date: 2026-10-11 (UTC). DATABASE_URL was unset, so no PDFs were downloaded and no corpus rows were written.

Sources (official Supreme Court of Georgia pages):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| Supreme Court Rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `79a76a9751b0f03c08ad8fb19655146da111ec50e88df13b9b35f4635b32002f` | 3 |
| Other court rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `410098ae3958141174a65c1458369ab6b915bf67d340d269f312f2783fe311df` | 7 |
| Other codes & rules index | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,606,015 | `35b129cd35d83a61b16adb3a9aa9659633c52c5dddcf9132bc335ac66aa42592` | 28 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

robots.txt Disallow: `/wp-content/uploads/`. All named PDFs live under that path, so none were fetched.

## Named PDF labels (not downloaded)

Supreme Court Rules:
- SupremeCourtRules_eff-July-2-2026.pdf
- CHART-WEB-POSTING-July-2-2026.pdf
- QUICK-REFERENCE-RULES.pdf

Other court rules:
- UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
- UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
- UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf
- UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
- UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
- UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- State-wide-Business-Court-Rules-2026_06_11.pdf

Other codes & rules: 28 PDF links named (including Code of Judicial Conduct, JQC rules, forms). Full list not expanded here; filenames are index labels only.

These are index checkpoints only. Filenames are not effective dates, not stored rule text, and not current-law verification. Court of Appeals rules pages returned WAF captcha on prior checks and were not re-fetched in this run. Lexis was not opened. No authority rows written.
