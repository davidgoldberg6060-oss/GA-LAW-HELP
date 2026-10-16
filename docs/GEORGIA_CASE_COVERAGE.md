Last production check: 2026-10-16 07:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals rules index, a sample rules page, and robots.txt. All returned AWS WAF captcha (HTTP 405). Page bytes were hashed; no rule text was extracted or stored; not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `61c944bfd27c54635cf43ec1b41adf5be88deaabe915aba0f17a1cc87d52ad64` | WAF captcha |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `b3bde0399c2932e8526799f26170298e0755cbe0c30a93f4b3630fde0ad99819` | WAF captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `7c988552f39fdedd431795b602137ab985d9ea13d056d809ec4de497d8e35cb8` | Same WAF page |

A browser-based fetch of the rules-1-8 page returned published rule text (effective March 26, 2026). That text was not persisted. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-coa-rules-waf.md`.

Last production check: 2026-10-16 06:19 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Secretary of State Rules and Regulations download page (https://rules.sos.ga.gov/Download_pdf.aspx) and robots.txt. Page bytes were hashed; department PDFs were not downloaded; not stored regulation text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| download page | https://rules.sos.ga.gov/Download_pdf.aspx | 200 | 163,973 | `36fca85cfbc0836a8b9afed0a2220c5a68693976115be7b1ac9164f1489e442f` | HTML index; current through September 17, 2026; ~154 department PDF labels |
| robots.txt | https://rules.sos.ga.gov/robots.txt | 200 | 3,628 | `c7ade8fc670dbef7bf1610f34f7b5484cd478e83cb35b67c2cd0456418d80fd0` | Allows department PDF downloads; disallows per-rule HTML |

The download page names approximately 154 unique department PDF labels. None were fetched. Lexis was not opened. Court of Appeals rules pages returned WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-sos-rules-download.md`.

Last production check: 2026-10-16 06:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court 2026 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no PDFs were downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,625,440 | `74b9a9afff701f4250fa25bad02ccedca46533cbb0885c4ca1c3d1dfcc61de5e` | 283 PDF anchors (274 docket-labeled); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

Raw fetch returned the year index page. 283 PDF link anchors named (274 with docket token). No opinion PDFs were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-2026.md`.

Last production check: 2026-10-15 22:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals opinion-search index and robots.txt. Page bytes were hashed; both returned the AWS WAF captcha; opinion PDFs were not downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a60e59e2e67412d10f9968a360c89a48e30fec247553546c59d17638a0c444c4` | WAF captcha; not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6f6c93f471077686c272395d6325401e3b5a5ff08eef110b11b082ad109867cb` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No docket-labeled PDF links were named. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15-appeals-opinion-search.md`.

Last production check: 2026-10-15 13:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `25e0c050ac996d061c246bf9b7e495327b03286c4ca0a92031ee876746d8b11b` | Manifest only; prior 2026-10-15 09:00 hash differed (834,799 bytes) |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15b-ocga-release86-manifest.md`. Court of Appeals rules index returned a WAF captcha on raw fetch (HTTP 405); rules pages were not stored. 

Last production check: 2026-10-15 09:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `1ce5785780a70001373f14954e8c27b0600cc4c83b97dbde5e4a305a72de940c` | Manifest only; prior 2026-10-10 hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15-ocga-release86-manifest.md`.

Last production check: 2026-10-13 16:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other-court-rules and rules indexes. Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,719 | `08411b3a60c162ce26230c41261c53990ba8068380065a201bc7d78e6dc04c32` | Index labels only |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,694 | `c60a61aeee1fe49912bbde1eb67feb622d213964609bbda77112d840e4dc4e6b` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

The other-court-rules index names 7 Uniform/other rule PDF links (Superior 2026-04-09, State 2024-01-18, Juvenile 2026-09-03, Probate 2023-06-01, Magistrate 2023-04-01, Municipal 2024-12-12, Statewide Business 2026-06-11). The rules index names the Supreme Court Rules PDF effective July 2, 2026 plus a chart and quick-reference PDF. robots.txt disallows `/wp-content/uploads/`, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Court of Appeals rules pages were not fetched in this pass. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-13-court-rules-indexes.md`.

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

Last production check: 2026-10-09 22:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2017 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2017 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2017 opinions index | https://www.gasupreme.us/2017-opinions/ | 200 | 1,654,787 | `5390aa94ccf5f61bec38bf63ddb8827054c56ad892b08f16a1f34374b963a51b` | 384 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 384 anchors and 369 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` does not refuse this year: no docket token maps to more than one PDF. A 19:00 UTC fetch of the same URL had the same byte count and a different SHA-256 (`e5e4c449cb0c57776090e3670424a35eac47250919d678b2ef400bc670d9438d`); label counts matched, so the page HTML is not stable. Nine kept anchors use a lowercase `_sub` filename, and two more use `_sub` with different letter case (S17A0255, S16Q1881). Two kept anchors use `_Reinstatement` and name companion dockets (S16Y1235, S16Y0723). Five other kept anchors do not match the PDF filename even case-insensitively (S17A0684 -> 17a0683_sub.pdf; S17G1491 -> s17c1491.pdf; S17Y1499 -> s17y1623.pdf; S17A1714 -> s17a0714.pdf; S16A1521 -> s16a1520.pdf). Two kept filenames match the docket only with different letter case (S17A0196, S17A0462). Twelve kept anchors name companion dockets on one URL. Fifteen extra docket-labeled anchors repeat a URL already kept by unique-URL dedupe. Twenty-three summary PDF anchors have no docket token; those were not counted as opinions (one links to s16a1716.pdf without a docket token in the label). Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2017.md`.

