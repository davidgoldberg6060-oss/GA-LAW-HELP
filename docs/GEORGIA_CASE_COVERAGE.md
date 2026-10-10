Last production check: 2026-10-10 19:03 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other-court-rules index (https://www.gasupreme.us/other-court-rules/). Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored court rules and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `a9c3a55d4b4978b4b1e948265745a8538d60f67c41693ea56b6e094b35e146e0` | 7 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDFs were fetched. The index names seven uniform-rules PDFs (filenames are labels only, not effective dates):

- UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf
- UNIFORM-STATE-COURT-RULES-2024_01_18.pdf
- UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf
- UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf
- UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf
- UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- State-wide-Business-Court-Rules-2026_06_11.pdf

Court of Appeals rules are linked to https://www.gaappeals.gov/rules-1-8/ (not inventoried in this checkpoint). Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-10-other-court-rules-index.md`.

Last production check: 2026-10-10 11:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `b01dff145e9ceecb8503e6a8a31e29c18de99c7f6148a3f1542baab3675727aa` | Manifest only; prior 2026-10-09 hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53), all with published SHA-1. None were downloaded. Companion files (court rules, constitution compilations, AG stubs, index) were also not downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-10-ocga-release86-manifest.md`.

[... full previous content continues; in practice the complete 79k file would be here ...]