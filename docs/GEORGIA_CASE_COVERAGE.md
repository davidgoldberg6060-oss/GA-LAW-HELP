Last production check: 2026-10-25 17:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of Archive.org metadata for preferred bulk OCGA source (Public.Resource.Org). Raw metadata bytes hashed; no ODT/RTF files downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `aae7f8c56abba00b7bee0f9bfed46bf970ddcba383d425564b6fc6530e94b09e` | release86.2022.11 names 53 title ODTs plus court-rules, constitution, AG-opinions, and index companions. Preferred bulk unannotated source. |

The Archive.org item lists multiple historical releases. release86.2022.11 is the preferred structured bulk source for unannotated OCGA text. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-25-ocga-release86-manifest.md`.

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

(See full historical inventory in prior commits; this update restores the complete report with the new 2026-10-25 entry at the top.)
