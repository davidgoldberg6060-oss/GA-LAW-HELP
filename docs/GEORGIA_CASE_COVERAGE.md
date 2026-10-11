Last production check: 2026-10-11 05:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the 2026 Georgia Supreme Court opinions index (https://www.gasupreme.us/2026-opinions/). Page bytes and robots.txt were hashed; opinion PDFs were not downloaded; not stored opinions and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,631,405 | `7bbc1e87b46dfc43e47cf56fa00369d61e0ba5ecdfd8faf74a04615247b64b57` | 263 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The index named 263 unique uploads PDF URLs. Of 263 PDF anchors, 254 contained a docket-style token. Nine summary-section anchors named PDFs without a clear docket token in the link text. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. Nested markup can split anchor text, so stored titles from the index label alone would be fragments. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-11-supreme-2026.md`.

Last production check: 2026-10-10 11:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `b01dff145e9ceecb8503e6a8a31e29c18de99c7f6148a3f1542baab3675727aa` | Manifest only; prior 2026-10-09 hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53), all with published SHA-1. None were downloaded. Companion files (court rules, constitution compilations, AG stubs, index) were also not downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-10-ocga-release86-manifest.md`.

Last production check: 2026-10-10 07:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Attorney General opinions index (https://law.georgia.gov/opinions). Page bytes and robots.txt were hashed; opinion PDFs were not downloaded; not stored opinions and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinions index | https://law.georgia.gov/opinions | 200 | 146,783 | `8a4730817fe28bccc7bcb9cd5344ee7b04e5fe808f32de22faeeefbe0102f874` | Index labels only |
| robots.txt | https://law.georgia.gov/robots.txt | 200 | 1,677 | `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b` | Allows /opinions |

The index names 46 opinion citation links (examples 2013-2 through 2026-2 and U-prefixed). Five document download links were present; none were fetched. Category indexes and later pagination were not walked. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-10-ag-opinions-index.md`.

Last production check: 2026-10-10 03:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia General Assembly annual general-statutes summary index (https://www.legis.ga.gov/general-statutes). Raw fetch returned the SPA shell (HTTP 200, 1,492 bytes, SHA-256 `05dd7a574b081f27c023001daa94e1f2f49a3f84151f0c6639ec54d7c691479a`). The rendered page titles itself "Annual Summary of Laws - Georgia General Assembly" and names 21 summary PDF links (2006–2026). Those PDFs were not downloaded. robots.txt returns the same SPA shell. The site's "Georgia Code" link points at LexisNexis (http://www.lexisnexis.com/hottopics/gacode); that host was not opened. These are session-summary labels, not unannotated OCGA section text and not current-law verification. The label list is in `ops/legal-import/2026-10-10-general-statutes-summaries.md`.
