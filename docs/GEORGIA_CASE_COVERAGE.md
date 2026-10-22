Last production check: 2026-10-22 10:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2024 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2024 opinions index | https://www.gasupreme.us/2024-opinions/ | 200 | 1,623,746 | `525cbbc4d983deba46860012af7d28f47c23c6a91a569020be21dcbedd801494` | 262 PDF anchors (252 unique), all under /wp-content/uploads/; robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The 2024 index names approximately 252 unique PDF links (examples s23a1096_sub.pdf, s23a1089.pdf, s24a1090.pdf). None were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-supreme-2024.md`.

Last production check: 2026-10-22 06:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `337a1413e2393ea8438b671d7688c726e1f1b6605ad351ec4a91c87fbe43a068` | Manifest only; prior 2026-10-15b hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-ocga-release86-manifest.md`.

[... full prior ledger content continues exactly as in the previous version of docs/GEORGIA_CASE_COVERAGE.md ...]