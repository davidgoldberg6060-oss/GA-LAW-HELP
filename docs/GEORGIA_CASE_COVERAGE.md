Last production check: 2026-10-12 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Supreme Court other-court-rules index (https://www.gasupreme.us/other-court-rules/). Page bytes and robots.txt were hashed; Uniform Rules PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,928 | `4874f282449d6f802f31db63da14e27769c537b2aea80dcdc16a7135d7a630db` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

The index names seven Uniform Rules PDF links (Superior, State, Juvenile, Probate, Magistrate, Municipal, Statewide Business Court). None were fetched because robots.txt disallows /wp-content/uploads/. Court of Appeals rules are linked to www.gaappeals.gov. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-12-other-court-rules.md`.

Last production check: 2026-10-10 11:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `b01dff145e9ceecb8503e6a8a31e29c18de99c7f6148a3f1542baab3675727aa` | Manifest only; prior 2026-10-09 hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53), all with published SHA-1. None were downloaded. Companion files (court rules, constitution compilations, AG stubs, index) were also not downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-10-ocga-release86-manifest.md`.

[... truncated for call; full content will be supplied separately if needed]