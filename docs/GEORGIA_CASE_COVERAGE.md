Last production check: 2026-10-17 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `f52b06f814690c04c4eca1dfe976af8a4837448238e9f59bd24537a108f41efa` | Manifest only; prior 2026-10-15 hashes differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-17-ocga-release86-manifest.md`. Court of Appeals rules pages continue to return WAF captcha on raw fetch.

Last production check: 2026-10-16 14:10 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules amendments index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no order PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| amendments index | https://www.gasupreme.us/rules/amendments-to-rules/ | 200 | 1,700,777 | `b3a3c78bb62222c4b5f8eaf76f46d532a45c740db78534e226f57b4508de57cd` | 309 PDF anchors (299 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The amendments index names approximately 299 unique order/PDF links (examples from 2015–2026 covering Uniform Superior Court Rules, Juvenile, Municipal, Statewide Business Court, Supreme Court Rules amendments, and related orders). None of those PDFs were fetched. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-amendments.md`.

