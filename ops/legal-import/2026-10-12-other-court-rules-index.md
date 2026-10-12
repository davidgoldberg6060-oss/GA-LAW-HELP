# Other court rules index — discover-only checkpoint

Fetch date: 2026-10-12 05:01 UTC. DATABASE_URL was unset, so no PDF files were downloaded and no corpus rows were written.

Source: https://www.gasupreme.us/other-court-rules/

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `b176d14c564e73bb47700a9bd37b8e227a66fcd6ba4ab77065dcd3030aadef2f` | Index HTML only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

The index names 7 Uniform / Statewide Business Court Rules PDF links. All live under `/wp-content/uploads/`, which robots.txt disallows, so none were fetched. Filenames include date stamps but are index labels only, not verified effective dates and not stored rule text.

## Named PDFs (not downloaded)

- https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
- https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
- https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf
- https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
- https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
- https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf

Gap notes: discover-only inventory of the official other-court-rules page. No rule text stored. Court of Appeals rules index (https://www.gaappeals.gov/court-rules/) returned AWS WAF captcha (HTTP 405) and was not inventoried. Lexis was not opened. These counts are not persisted coverage. A missing DATABASE_URL means no authority rows can be written.
