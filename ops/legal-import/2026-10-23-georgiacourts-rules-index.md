# 2026-10-23 Georgia Courts Supreme Court rules index checkpoint

DATABASE_URL was unset. Discover-only fetch of the Georgia Judicial Council / Administrative Office of the Courts page listing Supreme Court and related court rules (https://georgiacourts.gov/georgia-supreme-court-rules/). Index bytes were hashed; PDF targets under gasupreme.us/wp-content/uploads/ were not downloaded because robots.txt on gasupreme.us disallows that path. Not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `8fc27ecebaa34124a3ed2169192c825400992959bbb8ea00653afd47c2287cb3` | 28 PDF anchors, all under www.gasupreme.us/wp-content/uploads/; robots on gasupreme.us disallow /wp-content/uploads/ |

The index names 28 unique PDF links, including Supreme Court Rules (eff. 1.1.24 and later edits), redline/chart, Uniform Superior Court Rules 2024_02_29, Uniform State Court Rules 2024_01_18, Uniform Juvenile Court Rules 2022_05_06, Uniform Probate Court Rules 2023_06_01, Uniform Magistrate Court Rules 2023_04_01, Uniform Municipal Court Rules 2022_05_06, Statewide Business Court rules, Unified Appeal, Uniform Misdemeanor Citation, Uniform Transfer Rule, Rules for Legal Interpreting, Jury Composition Rule, JQC Rules, and others. None were fetched. Note that more recent versions appear on the gasupreme.us other-court-rules index (e.g., Superior 2026-04-09). Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
