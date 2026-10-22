# 2026-10-22 AG opinions index checkpoint (discover-only)

DATABASE_URL is unset, so no opinion PDFs or document downloads were fetched and no authority rows were written.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinions index | https://law.georgia.gov/opinions | 200 | 146,779 | `1f1f35613dd505ce3d78a13641d815c5011c5248c70b5c7ae9176d4d53094c7b` | Index labels only; 53 unique /opinions/ citation links |
| robots.txt | https://law.georgia.gov/robots.txt | 200 | 1,677 | `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b` | Allows /opinions |

Examples of named citations: 2013-2 through 2026-2, U-prefixed unofficial. Five document download links were present; none were fetched. Category indexes and later pagination were not walked. Lexis was not opened. These counts are not persisted coverage. Not stored opinion text and not current-law verification.
