Last production check: 2026-10-10 14:05 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia Rules index (https://www.gasupreme.us/rules/) and the former-rules page. Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored court-rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| current rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `3f7e7a80cb1bb297266d45d2ccf46792d66061e5f485ad7b1618d5946f557dab` | Index page only |
| former rules page | https://www.gasupreme.us/rules/former-rules/ | 200 | 1,707,016 | `e5d41324d9182e148083abde8f73adf3f3fcf2d9ed8420a6d191694a6caf385b` | Prior rule headings embedded |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

The index names three PDF links (current Rules effective July 2, 2026; 2026 amendment chart; Quick Reference). robots.txt disallows `/wp-content/uploads/`, so none were fetched. The former-rules page notes a January 1, 2024 amendment and embeds prior rule headings as HTML, not archived PDFs. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-10-supreme-rules-index.md`.

Last production check: 2026-10-10 11:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `b01dff145e9ceecb8503e6a8a31e29c18de99c7f6148a3f1542baab3675727aa` | Manifest only; prior 2026-10-09 hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53), all with published SHA-1. None were downloaded. Companion files (court rules, constitution compilations, AG stubs, index) were also not downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-10-ocga-release86-manifest.md`.

