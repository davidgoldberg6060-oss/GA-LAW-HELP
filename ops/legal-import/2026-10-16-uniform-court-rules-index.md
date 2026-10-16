# Uniform / other court rules index — discover-only checkpoint (2026-10-16)

Fetch date: 2026-10-16 10:03 UTC. DATABASE_URL is unset. No rule PDFs were downloaded. No authority rows were written. This is not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,586,219 | `69e215fd674431e26889eec29e466d92ab09fbfe0ae4c063a84250aaf6086e80` | HTML index; 7 PDF anchors named |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

## Named PDF labels (not downloaded)

| Label (index text) | URL |
| --- | --- |
| Rules (Superior) | https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf |
| Rules (State) | https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf |
| Rules (Juvenile) | https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf |
| Rules (Probate) | https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf |
| Magistrate Court | https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf |
| Municipal Court | https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf |
| Rules (Statewide Business Court) | https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDFs were fetched. Filenames are index labels, not effective dates, not stored rule text, and not current-law verification. Lexis was not opened. Court of Appeals rules index still returns AWS WAF captcha (HTTP 405) on raw fetch. These counts are not persisted coverage.

Gap notes: inventory of the index only. Rule PDFs remain unfetched because of robots disallow. Missing DATABASE_URL means no corpus rows can be written. Currency is unknown pending later official comparison against a non-disallowed source or authorized fetch.
