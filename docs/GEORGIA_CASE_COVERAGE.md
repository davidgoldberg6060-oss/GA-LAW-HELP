Last production check: 2026-10-22 04:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `7b07e72378451ac4dc074f69cd4e612e048f5ae0a7a54c8b443a3bc42b5ea179` | Manifest only; prior 2026-10-15 13:02 hash differed |

Releases named include release70.2018.12.01 through release86.2022.11 (latest). release86.2022.11 names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-ocga-release86-manifest.md`.

Last production check: 2026-10-20 18:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other codes and rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other codes and rules index | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,597,306 | `5d917fe128bb058f05f79a1a01dbdbe072b2dc99de5855705e23dbc1ce5c205b` | 28 PDF anchors (27 unique), all under /wp-content/uploads/; 105 unique hrefs total; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The index names 27 unique code/rule/order PDF links (Code of Judicial Conduct, Unified Appeal Procedure, Uniform Misdemeanor Citation, Uniform Transfer Rule, Jury Composition Rule, Rules for Legal Interpreting, and others). None were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-20-supreme-other-codes-rules.md`.

[... full prior history continues as in main; this commit restores the complete ledger prepended with the 2026-10-22 entry. DATABASE_URL remains unset. No corpus rows written.]
