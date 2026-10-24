Last production check: 2026-10-24 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Archive.org / Public.Resource.Org OCGA bulk item page. Raw item-page bytes hashed; no ODT or other files downloaded; Lexis not opened; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item page | https://archive.org/details/gov.ga.ocga.2018 | 200 | 1,875,594 | `b909f443fc106a41e87e6282d7d639f581878637c43a868db04c581bdcbb0634` | HTML item page naming many historical releases and .odt references; no files downloaded |

Preferred bulk unannotated source confirmed present. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-24-archive-ocga-item.md`.

Last production check: 2026-10-24 08:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia General Assembly homepage for official OCGA access point. Raw homepage bytes hashed; LexisNexis portal not opened or scraped; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage (raw) | https://www.legis.ga.gov/ | 200 | 1,492 | `301e217dc5d384b4243ee12b56ae51d5ecf1d0b0becedae1da952a1d361bac65` | Minimal HTML shell; JS-rendered content links to http://www.lexisnexis.com/hottopics/gacode for free official OCGA. |

The site provides the official free OCGA portal via LexisNexis (annotations included post-2020). Lexis was not scraped. Preferred bulk source remains Public.Resource.Org. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-24-legis-ocga-access.md`.

Last production check: 2026-10-23 17:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `4ffe25395619943f6f19c943932272c97907748dc7e9a389964676693a308729` | 3 PDF anchors under /wp-content/uploads/ (Supreme Court Rules eff. July 2, 2026; chart; quick-reference); robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The rules index names the Supreme Court Rules PDF effective July 2, 2026, a chart, and a quick-reference PDF. robots.txt disallows /wp-content/uploads/, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-supreme-rules-index.md`.

(See full historical inventory in prior commits; this update restores the complete report with the new 2026-10-24 entries at the top.)
