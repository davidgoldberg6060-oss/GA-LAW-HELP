Last production check: 2026-10-16 15:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `c198d0c8f80fd86030e9078ba7412333dc3c6cf9cb1625f556e0b936d828cde3` | Manifest only; prior 2026-10-15 13:02 hash differed (834,800 bytes) |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The detailed title inventory (names, sizes, SHA-1s) is in `ops/legal-import/2026-10-16-ocga-release86-titles.md`.

Last production check: 2026-10-16 14:10 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules amendments index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no order PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| amendments index | https://www.gasupreme.us/rules/amendments-to-rules/ | 200 | 1,700,777 | `b3a3c78bb62222c4b5f8eaf76f46d532a45c740db78534e226f57b4508de57cd` | 309 PDF anchors (299 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The amendments index names approximately 299 unique order/PDF links (examples from 2015–2026 covering Uniform Superior Court Rules, Juvenile, Municipal, Statewide Business Court, Supreme Court Rules amendments, and related orders). None of those PDFs were fetched. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-amendments.md`.

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

Last production check: 2026-10-09 17:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2018 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2018 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2018 opinions index | https://www.gasupreme.us/2018-opinions/ | 200 | 1,644,223 | `3471d0f750b42530592a8987dfdd04ae8b5e0b0dbdc46d20a6dffbe6f1d4da95` | 319 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 319 anchors and 316 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` refuses this year because S17A1905 points at both Mar518_Ops2.pdf and s17a1905.pdf. Five kept anchors use a `_Reinstatement` filename. Fourteen other kept anchors use `_sub`. Fifteen kept anchors name companion dockets on one URL. Three extra docket-labeled anchors repeat a URL already kept by unique-URL dedupe (S18A0725 shares s18a0725_sub.pdf; S18A0277 shares s18a0176.pdf with S18A0176; S18A0012 shares s18a0012.pdf). Twenty summary PDF anchors have no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2018.md`.

Last production check: 2026-10-09 16:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2019 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2019 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2019 opinions index | https://www.gasupreme.us/2019-opinions/ | 200 | 1,651,712 | `56203266f0ce8fc8055bc89667eedf8db3708eb470cfadf5a7c94c26876c2d58` | 344 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 344 anchors and 342 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` does not refuse this year: no docket token maps to more than one PDF. One kept anchor uses `_sub2` (S19A0231). Five kept anchors use a filename that is not a plain docket or `_sub` (S19C1007 -> s19g1007.pdf; S18Y0982 -> s18y0982_reinstatement.pdf; S18G1644 -> s18c1644.pdf; S19I1232 -> s18g1007.pdf; S17Y1532 -> s17y1532_reinstatement.pdf). Twelve other kept anchors use `_sub`. Twenty-one kept anchors name companion dockets on one URL. Two extra docket-labeled anchors repeat a URL already kept by unique-URL dedupe. Thirty-eight summary PDF anchors have no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2019.md`.

Last production check: 2026-10-09 15:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2020 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2020 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2020 opinions index | https://www.gasupreme.us/2020-opinions/ | 200 | 1,652,047 | `558e710ac33e46b962341fcc2ffd5a457367b12c87df7e520a84f02e56035a7e` | 348 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 348 anchors and 342 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` does not refuse this year: no docket token maps to more than one PDF. Five kept anchors use a filename suffix other than a plain docket or `_sub` (two `_sub2`, three `_Reinstatement`). Sixteen other kept anchors use `_sub`. Seventeen kept anchors name companion dockets on one URL. Six extra docket-labeled anchors repeat a URL already kept by unique-URL dedupe. Raw anchors also include 22 summary PDFs whose link text has no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2020.md`.

Last production check: 2026-10-09 14:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2021 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2021 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2021 opinions index | https://www.gasupreme.us/2021-opinions/ | 200 | 1,632,494 | `74d1c94e690392a74fc9f06256ced743eeb9e88d4eb73cb779095dc6ad9360ef` | 238 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 238 anchors and 236 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` does not refuse this year: no docket token maps to more than one PDF. One kept anchor does not match the PDF filename (S21G0167 -> s21c0167.pdf). Nineteen kept anchors name companion dockets on one URL. Two extra docket-labeled anchors repeat a URL already kept by unique-URL dedupe. Raw anchors also include 22 summary PDFs whose link text has no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2021.md`.

Last production check: 2026-10-09 13:02 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2022 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2022 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2022 opinions index | https://www.gasupreme.us/2022-opinions/ | 200 | 1,629,465 | `b88c7535d7b05d397c778caf1ccbcbdaade42c8c28237b69d59a85dfface0730` | 221 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 221 anchors and 221 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` does not refuse this year: no docket token maps to more than one PDF. Two kept anchors do not match the PDF filename (S19Z1369 -> document-16.pdf; S21H0656 -> s22a1020.pdf, which matches companion token S22A1020). Thirteen kept anchors name companion dockets on one URL. Raw anchors also include 22 summary PDFs whose link text has no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2022.md`.

Last production check: 2026-10-09 12:02 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2025 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2025 opinions index | https://www.gasupreme.us/2025-opinions/ | 200 | 1,633,450 | `ebd008eb60fad33a8d636711806790f9c9e9f869292d0ef71a2c94160a6d472e` | 250 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 250 anchors and 247 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` does not refuse this year: no docket token maps to more than one PDF. Three pairs of distinct captions share one URL and unique-URL dedupe would keep only the first caption (S25A0058/S25A0150, S25A0249/S25A0250, S24A1303/S24A1304). Raw anchors also include summary PDFs whose link text has no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2025.md`.

Last production check: 2026-10-09 09:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2023 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2023 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2023 opinions index | https://www.gasupreme.us/2023-opinions/ | 200 | 1,629,592 | `58d21310a0f71dab19a4a860335983937f07c245ad1a4ef57189aa6ded1ce1ec` | 219 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 219 anchors and 218 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. `parse_index` refuses this year because S21Z0595 and S23Y0434 each point at more than one PDF. One anchor token (S23C0795) does not match its PDF filename. Raw anchors also include summary PDFs whose link text has no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2023.md`.

Last production check: 2026-10-09 07:05 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2024 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2024 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2024 opinions index | https://www.gasupreme.us/2024-opinions/ | 200 | 1,632,385 | `d75f735e1dd46349187900a31c94927170a0b1da7bf0d36d185c03ef75943262` | 231 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The importer's docket rule named 231 unique uploads PDF URLs. robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. Raw anchors also include summary PDFs whose link text has no docket token; those were not counted as opinions. Nested markup splits some anchor text, so stored titles would be fragments if imported from the index label alone. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-09-supreme-2024.md`.

Last production check: 2026-10-09 06:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_appeals_opinions --discover-only --commit` was refused and no corpus rows were written. Discover-only read of the Court of Appeals opinion-search page and robots.txt only (response bytes hashed; date-search endpoint not requested; efast opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| opinion search page | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `9194866ac226fac09ec04b679585578cf12ed2a3c6ea7340fc46eb34714186d8` | 0 |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `b215ca70f33fde33a0f23f5e1e77100f48f016ae9f849da93269054ccb510aa0` | 0 |

Both responses were AWS WAF Human Verification pages, not the court index or robots file. The SHA-256 values are of those captcha responses and will change on the next fetch. No docket labels or PDF URLs were named. `results_all.php` and `efast.gaappeals.gov` were not requested. Lexis was not opened. These counts are not persisted coverage.

Last production check: 2026-10-09 05:05 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2026 --discover-only --forthcoming --commit` was refused and no corpus rows were written. Discover-only read of the official forthcoming-opinions index (page bytes and PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| forthcoming opinions | https://www.gasupreme.us/forthcoming-opinions/ | 200 | 1,596,305 | `237773d05120a1d28af09c2690c794f36e277fa649abcb6f1e2e1b691478a91f` | 10 |
| 2016 annual index | https://www.gasupreme.us/2016-opinions/ | 404 | 1,588,085 | `5a87fe8d2035a87891e96fbaae71d6889b344db17a7b09968f964e96559db394` | 0 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

`/opinions/forthcoming-opinions/` redirected to `/forthcoming-opinions/`. robots.txt disallows `/wp-content/uploads/`, so every named PDF stayed unfetched. The 2016 annual index is a WordPress 404; the importer still starts at 2017. Court of Appeals `/opinion-search/` returned HTTP 405 from this environment, so no appeals opinion index was read. Lexis was not opened. These counts are not persisted coverage.

| Docket label | PDF URL | Gap |
| --- | --- | --- |
| S25G1446, S25G1447. CRAVENS v. SLAUGHTER et al. (two cases) | https://www.gasupreme.us/wp-content/uploads/2026/09/s25g1446.pdf | Index label only; PDF not downloaded; companion docket shares one URL; not stored text |
| S26A0604. WARE v. THE STATE | https://www.gasupreme.us/wp-content/uploads/2026/09/s26a0604.pdf | Index label only; PDF not downloaded; not stored text |
| S26A0732. WALKER v. THE STATE | https://www.gasupreme.us/wp-content/uploads/2026/09/s26a0732.pdf | Index label only; PDF not downloaded; not stored text |
| S26A0769. LOWE v. THE STATE | https://www.gasupreme.us/wp-content/uploads/2026/09/s26a0769.pdf | Index label only; PDF not downloaded; not stored text |
| S26A0775. GAMBLE v. THE STATE | https://www.gasupreme.us/wp-content/uploads/2026/09/s26a0775.pdf | Index label only; PDF not downloaded; not stored text |
| S26A1003. REYNOLDS v. THE STATE | https://www.gasupreme.us/wp-content/uploads/2026/09/s26a1003.pdf | Index label only; PDF not downloaded; not stored text |
| S26A1067. WILSON v. THE STATE | https://www.gasupreme.us/wp-content/uploads/2026/09/s26a1067.pdf | Index label only; PDF not downloaded; not stored text |
| S26A1488. MARTIN v. THE STATE | https://www.gasupreme.us/wp-content/uploads/2026/09/s26a1488.pdf | Index label only; PDF not downloaded; not stored text |
| S24Z1139, S25Z0722. INQUIRY CONCERNING JUDGE SHERMELA J. WILLIAMS (two cases) | https://www.gasupreme.us/wp-content/uploads/2026/09/s24z1139.pdf | Index label only; PDF not downloaded; companion docket shares one URL; not stored text |
| S26Y0982. IN THE MATTER OF JAMES A. SATCHER JR. | https://www.gasupreme.us/wp-content/uploads/2026/09/s26y0982.pdf | Index label only; PDF not downloaded; not stored text |

Oral-argument calendar JSON on the same page names other dockets (including S25G1349 and S26G1200). Those are not opinion PDF links and were not fetched.

Last production check: 2026-10-09 02:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_ocga_release --release release86.2022.11 --discover-only --commit` was refused and no corpus rows were written. Discover-only read of archive.org metadata for item `gov.ga.ocga.2018` (file names, sizes, and published SHA-1 only; title ODTs not downloaded; not stored authorities and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | Title ODTs named |
| --- | --- | ---: | ---: | --- | ---: |
| archive.org metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `2eb98d64486d5f14e3daf6347003b449c4f427afa6cbadee99e741551e613142` | 53 |

The same metadata URL was hashed on 2026-10-08 as `6932b465976fad58e8aec931b1c67f7d1079b59af79c7ef352512c1c61b174d6` at the same byte count. The hash changed, so these published SHA-1 values must be re-checked before any title download. No title file was fetched. Lexis was not opened. These counts are not persisted coverage.

| Title | File | Bytes | Published SHA-1 | Gap |
| ---: | --- | ---: | --- | --- |
| 1 | [gov.ga.ocga.title.01.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.01.odt) | 151,683 | `7f1c767bda5c596515b56638295858453675871c` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 2 | [gov.ga.ocga.title.02.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.02.odt) | 314,047 | `0ba693ed788e23120b116a0a32ba3d162727eee1` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 3 | [gov.ga.ocga.title.03.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.03.odt) | 196,516 | `0791d0938be89e4cb7acc6085073c25891f8c977` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 4 | [gov.ga.ocga.title.04.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.04.odt) | 117,674 | `0f1c093a2659ad9319456d4a2103854f7bc967f6` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 5 | [gov.ga.ocga.title.05.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.05.odt) | 772,483 | `4b53d491dcdad9860999de2b952b1b067d284dee` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 6 | [gov.ga.ocga.title.06.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.06.odt) | 41,120 | `1154cf10ca36e3cba28ecb8d6d6424289256d3cf` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 7 | [gov.ga.ocga.title.07.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.07.odt) | 599,971 | `887b1d46107e1101272a5a6285db8c80dae626df` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 8 | [gov.ga.ocga.title.08.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.08.odt) | 162,817 | `29be57e49fea02c3c26c903fc62f1f025bd27b66` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 9 | [gov.ga.ocga.title.09.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.09.odt) | 2,886,628 | `9f835884da1574eaba955673e5cd5a275e2714f0` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 10 | [gov.ga.ocga.title.10.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.10.odt) | 1,077,445 | `c82147fa77114c5c175b138780adc436bac639e3` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 11 | [gov.ga.ocga.title.11.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.11.odt) | 733,270 | `ffe920deb5c79e4484528f10dcb80b6fa052a2a8` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 12 | [gov.ga.ocga.title.12.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.12.odt) | 832,493 | `cf775cafbd5b5a8a9eb6ac9ba0bf66f31b7e43c8` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 13 | [gov.ga.ocga.title.13.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.13.odt) | 863,613 | `e6abcf43e902cebaaa099b909f980eed015a290a` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 14 | [gov.ga.ocga.title.14.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.14.odt) | 908,409 | `7542c20f973eda7b1a5b0792ddd61bf87c231d8b` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 15 | [gov.ga.ocga.title.15.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.15.odt) | 1,668,827 | `1b2f2df9d0a9967e827a20cc2f229238fedb0aab` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 16 | [gov.ga.ocga.title.16.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.16.odt) | 3,382,207 | `fc0de710946f43d0d1a588651db2fd29ef174c49` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 17 | [gov.ga.ocga.title.17.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.17.odt) | 1,646,017 | `ac725ac4cba54739e00bfee89481ea77767027e0` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 18 | [gov.ga.ocga.title.18.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.18.odt) | 221,792 | `f34e39a1eff7daa387a53eab8587da70db5dbec7` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 19 | [gov.ga.ocga.title.19.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.19.odt) | 936,277 | `e94034ec8905b3e54597054d8661ad1f4b2f396f` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 20 | [gov.ga.ocga.title.20.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.20.odt) | 1,076,479 | `8b2b59c715fd0587f181896cc1c12da7dbdcd60b` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 21 | [gov.ga.ocga.title.21.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.21.odt) | 539,155 | `0464c4187409e6137a03a15cf0b486e6a22d925b` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 22 | [gov.ga.ocga.title.22.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.22.odt) | 172,570 | `786935f74e990c978256e09f141cc3c32d357aac` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 23 | [gov.ga.ocga.title.23.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.23.odt) | 363,503 | `c6b3f48ff22ce7a116055682873ddeeac2674013` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 24 | [gov.ga.ocga.title.24.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.24.odt) | 1,682,900 | `3a660fc0ef3b9609c2dd677af9ea087b5e2ebe5f` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 25 | [gov.ga.ocga.title.25.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.25.odt) | 173,044 | `5cdd2c87f1e52ce44339d294d9f80a378be8fa7c` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 26 | [gov.ga.ocga.title.26.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.26.odt) | 244,609 | `613be9ee4996cb2c637a0c2bb74472a0558b4a22` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 27 | [gov.ga.ocga.title.27.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.27.odt) | 210,894 | `7b8b0e6e3a3755f6d86784f410e369f995352d54` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 28 | [gov.ga.ocga.title.28.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.28.odt) | 76,491 | `7f8d7aac9b9a51f439226a8d5165d11c059e3db7` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 29 | [gov.ga.ocga.title.29.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.29.odt) | 265,989 | `82c0034c04ae9d270b694bd5487b60fe32045a78` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 30 | [gov.ga.ocga.title.30.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.30.odt) | 59,546 | `ff92806e6bf19c19419cbbc01a74ee3eaeea0ab4` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 31 | [gov.ga.ocga.title.31.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.31.odt) | 701,856 | `81d606c33605dd0ab644e25b7acdbed54a6c96c0` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 32 | [gov.ga.ocga.title.32.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.32.odt) | 379,392 | `4201bfd54a342b696b574f819594b7e9c89db2a5` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 33 | [gov.ga.ocga.title.33.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.33.odt) | 1,529,299 | `8f2d85ab54bdb5eb57b8906af3b06609487c3aae` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 34 | [gov.ga.ocga.title.34.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.34.odt) | 1,035,444 | `09200b055c6c3e7026b08d44b387084aaadd6299` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 35 | [gov.ga.ocga.title.35.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.35.odt) | 195,547 | `c3ecaca536a6ed1f00a896baa1952e763777d6f3` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 36 | [gov.ga.ocga.title.36.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.36.odt) | 883,500 | `c4b55ef26589d4bcb160d7071047a671536b3f68` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 37 | [gov.ga.ocga.title.37.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.37.odt) | 273,901 | `f0f89f24ea545f6229f57aef106c10904f9b684d` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 38 | [gov.ga.ocga.title.38.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.38.odt) | 190,871 | `45306c0ac89b64b0cef031d04197fecf487c7a1a` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 39 | [gov.ga.ocga.title.39.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.39.odt) | 22,647 | `a4ae4396aa18c13d345ee253c6ade01208d8d9a5` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 40 | [gov.ga.ocga.title.40.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.40.odt) | 1,260,886 | `eb47c76dee6bc348bca40051a743a4c5ea11dc04` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 41 | [gov.ga.ocga.title.41.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.41.odt) | 85,095 | `8c287467e7c3c9cab1be9e88f9a92c9606358d94` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 42 | [gov.ga.ocga.title.42.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.42.odt) | 471,503 | `0ac38f6b6c3a6167bd0c1f79d0a50815fb6f8c5b` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 43 | [gov.ga.ocga.title.43.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.43.odt) | 1,112,011 | `49203169f6966bac4f5c89943ca513f92f5e4a73` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 44 | [gov.ga.ocga.title.44.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.44.odt) | 1,781,346 | `a84d021831eb522a63cd7675818555dacb14cc0b` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 45 | [gov.ga.ocga.title.45.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.45.odt) | 503,981 | `989687ce07c22ecbb022c3e17216e67449250387` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 46 | [gov.ga.ocga.title.46.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.46.odt) | 637,679 | `b5627c15146a37f97808b6fbd64b9a0bb93df7ec` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 47 | [gov.ga.ocga.title.47.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.47.odt) | 498,817 | `33c91cefeec9624103e138d6a57c7d612f3c0278` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 48 | [gov.ga.ocga.title.48.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.48.odt) | 1,529,531 | `cdd2ce267ea99ffc0e96cc6bd26a1ecaba1a61df` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 49 | [gov.ga.ocga.title.49.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.49.odt) | 302,883 | `01c2f201e1f6e80e215cb39148a1c227e8c3b5c9` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 50 | [gov.ga.ocga.title.50.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.50.odt) | 946,734 | `69a1bdd6d8bbfc1e289a39acd241f3b95b0f3b18` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 51 | [gov.ga.ocga.title.51.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.51.odt) | 1,305,409 | `060c59ea764e9023e0a0873749e10bf7f8841548` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 52 | [gov.ga.ocga.title.52.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.52.odt) | 123,731 | `6f235543ea9286f33f13e871c06fe9b7a6a0c31d` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |
| 53 | [gov.ga.ocga.title.53.odt](https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.53.odt) | 636,010 | `ac8ed2dee0046752340ef56b0d993b602bfd3fbf` | Manifest checksum only; ODT not downloaded; not stored text; as-of 2022-11 is not current law |


Last production check: 2026-10-09 00:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_ag_opinions --discover-categories --commit` was refused and no corpus rows were written. Discover-only hashes of the official Attorney General category indexes (page bytes and citation-label counts only; PDFs not downloaded; not stored opinions and not current-law verification):

| Category | URL | HTTP | Bytes | SHA-256 | Labels | PDF links named |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| official | https://law.georgia.gov/opinions/official | 200 | 144,464 | `109b04215fde567eb8fffd533ba0c279cb6b2d4282b7890f1cac82a5018a9814` | 50 | 4 |
| official | https://law.georgia.gov/opinions/official?page=1 | 200 | 143,780 | `ce54e2d15f781b1aa3b3587aba516f42ef95fd1ff86ca97a9b22b7165fea2c59` | 50 | 0 |
| official | https://law.georgia.gov/opinions/official?page=2 | 200 | 140,561 | `fcd0a205ebf2330e507b2da5bab1fd438d9d8f95d3b11f6c9959ad91472f50af` | 50 | 0 |
| official | https://law.georgia.gov/opinions/official?page=3 | 200 | 141,408 | `921c06b33412ad32df418a75142944e45b8ff8a09a1b596ed2315c4fb8608f37` | 50 | 0 |
| official | https://law.georgia.gov/opinions/official?page=4 | 200 | 140,249 | `2c7316e54ddf4a83f68ffa44b34907ad1c8791125257457d461bb3f1d30a73d0` | 50 | 0 |
| official | https://law.georgia.gov/opinions/official?page=5 | 200 | 139,524 | `25c1f0c9d1e16c6eb0c120cc0c3c39aafd0bbcbb78b39073efd3ff37ce96ea52` | 50 | 0 |
| official | https://law.georgia.gov/opinions/official?page=6 | 200 | 112,161 | `7c7f26da7c5ea01e53c8308fd84e2b037970db5d110398fe698a466284809fc4` | 21 | 0 |
| unofficial | https://law.georgia.gov/opinions/unofficial | 200 | 142,165 | `737942699d0b0bb2ad2517c948e029c23819fc5100ab31f2e7939517d505549f` | 50 | 1 |
| unofficial | https://law.georgia.gov/opinions/unofficial?page=1 | 200 | 139,803 | `cf2a97a781f569af2af8d0dfc43db5fae3dec0423f24d77e8658c8e109de19d3` | 50 | 0 |
| unofficial | https://law.georgia.gov/opinions/unofficial?page=2 | 200 | 140,053 | `a5e1df183e48e1c33f3d8e828326972ba5663ab8deccf6ba2e4172f62c139f5e` | 50 | 0 |
| unofficial | https://law.georgia.gov/opinions/unofficial?page=3 | 200 | 140,964 | `a4313ea8f80c1418451e76006c6ffa36926b4fca90161d2f7babc32d04ba816b` | 50 | 0 |
| unofficial | https://law.georgia.gov/opinions/unofficial?page=4 | 200 | 107,011 | `35be77f3b5dd8821861874735572ac10396bebd3cd2e98fd8fb14a91c493797b` | 16 | 0 |
| obsolete-and-modified | https://law.georgia.gov/opinions/obsolete-and-modified-opinions | 200 | 91,323 | `36bc7f5d548498e3d86adbcc2d56979af9b431e35270010ec5f5aa6642442e7b` | 0 | 1 |

Official page 0 names labels `2026-2` through `2024-1` among 50 labels. Unofficial page 0 names `U2026-1` among 50 labels. Combined label counts are 321 official and 216 unofficial. The obsolete page names no citation label; it links `https://law.georgia.gov/document/publication/obsoleteandmodifiedopinionsthroughaugust2016pdf/download` (filename says through August 2016). That PDF was not fetched. Official page 0 also names `https://law.georgia.gov/document/document/032426-official-ag-opinionpdf--UNPUBLISHED-document--DO-NOT-SHARE-this-URL--/download`; that URL was not fetched. `https://law.georgia.gov/opinions?page=11` returned HTTP 200 (93,601 bytes, SHA-256 `5666188473f79e98b739c44ef9e418b6bce5f4e97fce94cfed2a481511e3fa04`) and named no citation labels, so the main index tail after page 10 is empty. These counts are not persisted coverage.

Last production check: 2026-10-08 22:05 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_ag_opinions --commit` was refused and no corpus rows were written. Discover-only hashes of the official Attorney General opinion index (page bytes and citation labels only; PDFs not downloaded; not stored opinions and not current-law verification):

| Page | URL | HTTP | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| 0 | https://law.georgia.gov/opinions | 200 | 146,784 | `89adba418f9312da28c9ee3ea233d62654ef52524a940b7cf95f251265d76ba4` |
| 1 | https://law.georgia.gov/opinions?page=1 | 200 | 142,536 | `444bce0bd0500a7be7853c42bad5902e1279c2bbdc6c00ca60cf2455c0b5b1f4` |
| 2 | https://law.georgia.gov/opinions?page=2 | 200 | 144,532 | `fc3d6875d0412e0f669630023a5214944df451e80d551bfc8331b0013a283d92` |
| 3 | https://law.georgia.gov/opinions?page=3 | 200 | 142,010 | `f2eadfe3e0ffed26e5348a206229ec9fd09e58bcfe11b16360060dd6e4724e4a` |
| 4 | https://law.georgia.gov/opinions?page=4 | 200 | 142,009 | `80351d668665876e56759da7792b9fdbbaabd59a58a0ddbb4a60c8bb87c5c4bd` |
| 5 | https://law.georgia.gov/opinions?page=5 | 200 | 141,290 | `68c0c69c2575014cd19c0ffc5ab20f28f07e54f0a01fb3783fca1e58cba8a02c` |
| 6 | https://law.georgia.gov/opinions?page=6 | 200 | 140,727 | `8a3d4464e78be01781d0a0f0368c7d0b71b44ed1a46ade5a11e96138ca344b07` |
| 7 | https://law.georgia.gov/opinions?page=7 | 200 | 141,651 | `5de76402e2d7ca67d59fd5e600798245ee69a5b81ad9ee6c1791b2ff0a02ce4f` |
| 8 | https://law.georgia.gov/opinions?page=8 | 200 | 142,488 | `430dc744ee19a7c2ab4a22ab7093dfeec03b9a8a96b1e59156582bdd104bbaca` |
| 9 | https://law.georgia.gov/opinions?page=9 | 200 | 140,541 | `ab2b0763b615d069c560199cb7906cf2be56d102c75aab293dc8580a0d6e210c` |
| 10 | https://law.georgia.gov/opinions?page=10 | 200 | 126,949 | `012ea1150b5db648a5429e6530380e14594085981d79e56d59ee008a3ed0d694` |

`https://law.georgia.gov/robots.txt` returned HTTP 200 (1,677 bytes, SHA-256 `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b`) and does not disallow `/opinions` or `/document/`. Page 0 names five PDF download links. One of those URLs contains `UNPUBLISHED-document--DO-NOT-SHARE`; that file was not fetched. Pages 1-10 name citation labels (about 2026 through 1992 on the last page) without PDF links in the index HTML. Labels are index checkpoints, not opinion text. The importer `--discover-only` path lists those labels and refuses `--commit` while DATABASE_URL is unset. These counts are not persisted coverage.

Last production check: 2026-10-08 20:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_court_rules --discover-other-codes` was not run with `--commit` and no corpus rows were written. Discover-only read of the official other-codes-and-rules index (page bytes and PDF filenames only; PDFs not downloaded; not stored rules and not current-law verification):

| Index | HTTP | Bytes | SHA-256 | Official PDF links |
| --- | ---: | ---: | --- | ---: |
| https://www.gasupreme.us/other-codes-rules/ | 200 | 1,603,773 | `c1e342e7c3be85988a16e918dd946aa7bf166c2969350926a816134e00728281` | 27 |

`https://www.gasupreme.us/robots.txt` still disallows `/wp-content/uploads/` (71 bytes, SHA-256 `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196`). Every PDF below is linked under that path, so the importer reports them as blocked checkpoints and does not fetch them. Filenames are index labels, not verified effective dates. Lexis was not opened. Court of Appeals `/opinions/` and `/` still returned HTTP 405 with a captcha challenge, so no appeals opinion index was read. These counts are not persisted coverage.

| File | URL |
| --- | --- |
| georgia_code_judicial_conduct_revised_5-14-15.pdf | https://www.gasupreme.us/wp-content/uploads/2015/06/georgia_code_judicial_conduct_revised_5-14-15.pdf |
| Order_CJC_FINAL.pdf | https://www.gasupreme.us/wp-content/uploads/2016/09/Order_CJC_FINAL.pdf |
| Order_CJC_REDLINE-.pdf | https://www.gasupreme.us/wp-content/uploads/2016/09/Order_CJC_REDLINE-.pdf |
| UNIFIED_APPEAL-06_06_18.pdf | https://www.gasupreme.us/wp-content/uploads/2018/06/UNIFIED_APPEAL-06_06_18.pdf |
| CODE_OF_JUDICIAL_CONDUCT_AMENDMENT_ORDER_OCTOBER_22_2018.pdf | https://www.gasupreme.us/wp-content/uploads/2018/10/CODE_OF_JUDICIAL_CONDUCT_AMENDMENT_ORDER_OCTOBER_22_2018.pdf |
| Uniform_Misdemeanor_Citation_Approval_Order_dec_2018.pdf | https://www.gasupreme.us/wp-content/uploads/2018/12/Uniform_Misdemeanor_Citation_Approval_Order_dec_2018.pdf |
| Uniform_Misdemeanor_Citation_Form-_FINAL_ADOPTED_12-7-18.pdf | https://www.gasupreme.us/wp-content/uploads/2018/12/Uniform_Misdemeanor_Citation_Form-_FINAL_ADOPTED_12-7-18.pdf |
| Uniform_Misdemeanor_Citation_Rules_FINAL_ADOPTED_12-7-18.pdf | https://www.gasupreme.us/wp-content/uploads/2018/12/Uniform_Misdemeanor_Citation_Rules_FINAL_ADOPTED_12-7-18.pdf |
| Uniform_Transfer_Rule_Adopted_Judicial_Council_12-7-2018-_FINAL.pdf | https://www.gasupreme.us/wp-content/uploads/2018/12/Uniform_Transfer_Rule_Adopted_Judicial_Council_12-7-2018-_FINAL.pdf |
| Uniform_Misdemeanor_Citation_Approval_Order_jul_2019.pdf | https://www.gasupreme.us/wp-content/uploads/2019/02/Uniform_Misdemeanor_Citation_Approval_Order_jul_2019.pdf |
| Uniform_Misdemeanor_Citation_Rules_FINAL_REVISED_07-01-2019.pdf | https://www.gasupreme.us/wp-content/uploads/2019/02/Uniform_Misdemeanor_Citation_Rules_FINAL_REVISED_07-01-2019.pdf |
| JURY_COMPOSITION_RULE_2019-04-11.pdf | https://www.gasupreme.us/wp-content/uploads/2019/04/JURY_COMPOSITION_RULE_2019-04-11.pdf |
| Civil_Domestic_Filing_Disposition_Form-FINAL-eff-010120.pdf | https://www.gasupreme.us/wp-content/uploads/2019/08/Civil_Domestic_Filing_Disposition_Form-FINAL-eff-010120.pdf |
| order-amending-CJC-Terminology-section-definition-of-law-Issued.pdf | https://www.gasupreme.us/wp-content/uploads/2020/07/order-amending-CJC-Terminology-section-definition-of-law-Issued.pdf |
| Statewide-Min-Standards-Rules-final.pdf | https://www.gasupreme.us/wp-content/uploads/2020/10/Statewide-Min-Standards-Rules-final.pdf |
| Order-_-Amended-Rules-for-LegaInterpreting.pdf | https://www.gasupreme.us/wp-content/uploads/2024/01/Order-_-Amended-Rules-for-LegaInterpreting.pdf |
| Code-of-Judicial-Conduct-2024_02_01.pdf | https://www.gasupreme.us/wp-content/uploads/2024/02/Code-of-Judicial-Conduct-2024_02_01.pdf |
| Rule-2.5-order_final_issued_1.pdf | https://www.gasupreme.us/wp-content/uploads/2024/02/Rule-2.5-order_final_issued_1.pdf |
| RulesForLegalInterpreting_updatedMarch2025.pdf | https://www.gasupreme.us/wp-content/uploads/2025/03/RulesForLegalInterpreting_updatedMarch2025.pdf |
| 2026-UAP-amendments-Final-Order_entered.pdf | https://www.gasupreme.us/wp-content/uploads/2025/12/2026-UAP-amendments-Final-Order_entered.pdf |
| Order_Amend-Part-A-Fitness-Board-Membership_issued.pdf | https://www.gasupreme.us/wp-content/uploads/2025/12/Order_Amend-Part-A-Fitness-Board-Membership_issued.pdf |
| JQC-RULES-2023_02_03.pdf | https://www.gasupreme.us/wp-content/uploads/2026/03/JQC-RULES-2023_02_03.pdf |
| JQC-Rules-Amendment-Approval-Order_entered_sub.pdf | https://www.gasupreme.us/wp-content/uploads/2026/03/JQC-Rules-Amendment-Approval-Order_entered_sub.pdf |
| JQC_Final_Rules_Order.pdf | https://www.gasupreme.us/wp-content/uploads/2026/03/JQC_Final_Rules_Order.pdf |
| JQC_Interim_Rules_Order_06-28-17.pdf | https://www.gasupreme.us/wp-content/uploads/2026/03/JQC_Interim_Rules_Order_06-28-17.pdf |
| JQC_RULES_AMENDMENT_ORDER_OCTOBER_22_2018.pdf | https://www.gasupreme.us/wp-content/uploads/2026/03/JQC_RULES_AMENDMENT_ORDER_OCTOBER_22_2018.pdf |
| Replacement-Citizen-Order_entered.pdf | https://www.gasupreme.us/wp-content/uploads/2026/03/Replacement-Citizen-Order_entered.pdf |

Last production check: 2026-10-08 19:05 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_ocga_release --release release86.2022.11 --commit` was not run and no corpus rows were written. Discover-only read of archive.org metadata for item `gov.ga.ocga.2018` (file names, sizes, and published SHA-1 only; companion files not downloaded; not stored authorities and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| archive.org metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `6932b465976fad58e8aec931b1c67f7d1079b59af79c7ef352512c1c61b174d6` |

Companion files named in `release86.2022.11` besides the 53 title ODTs (published checksums are file checkpoints, not text):

| File | Bytes | Published SHA-1 | Gap |
| --- | ---: | --- | --- |
| gov.ga.ocga.constitution.ga.odt | 1,804,968 | `b37dfc34a98e2103ea588743a605e12136a08756` | Georgia constitution compilation in this release; not downloaded; not a current-law check; Lexis not opened |
| gov.ga.ocga.constitution.us.odt | 1,719,677 | `b53d02725edb45e9ce5c8e1fafa7d60d8566cdfb` | United States constitution copy; not Georgia authority text; not downloaded |
| gov.ga.court.rules.odt | 3,026,291 | `4610a0430d2d6a6dabf67ce569a589bfb0a6a84a` | 2022-11 release court-rules file; not the later gasupreme.us PDFs; not downloaded |
| gov.ga.court.rules.index.odt | 123,188 | `0a499e7d7ff0e89e1af0642489c0082586b1ece6` | Index file, not authority text; not downloaded |
| gov.ga.ocga.index.odt | 6,035,845 | `2e7eaf2529d7281864b409bcb1393157cd6e8487` | Index file, not authority text; not downloaded |
| gov.ga.ag.2020.opinions.odt | 6,315 | `7f01267e4ee10050ed02458a245a1106fe8793a5` | Same published SHA-1 as the 2022 AG file; not downloaded; not opinion text |
| gov.ga.ag.2022.opinions.odt | 6,315 | `7f01267e4ee10050ed02458a245a1106fe8793a5` | Same published SHA-1 as the 2020 AG file; not downloaded; not opinion text |

Matching RTF companions are named in the same manifest and were not downloaded. The importer discover report now lists these companion URLs, sizes, published SHA-1 values, and gap notes, and still refuses `--discover-only` with `--commit`. These counts are not persisted coverage.

Last production check: 2026-10-08 18:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_court_rules --set municipal,business` was not run with `--commit` and no corpus rows were written. Discover-only re-read of the official other-court-rules index (page bytes and PDF filenames only; PDFs not downloaded; not stored rules and not current-law verification):

| Index | HTTP | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,752 | `d470b95a30b87117d95c845395acc36e27a488552942e394fb71920ad08488d4` |

Official PDF links named on that page (uploads remain disallowed by robots.txt; filenames are index labels, not verified effective dates):

| Set | PDF URL | In importer before this checkpoint |
| --- | --- | --- |
| superior | https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf | yes |
| state | https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf | yes |
| juvenile | https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf | yes |
| probate | https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf | yes |
| magistrate | https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf | yes |
| municipal | https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf | added as blocked checkpoint only |
| business | https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf | added as blocked checkpoint only |

`https://www.gasupreme.us/robots.txt` still disallows `/wp-content/uploads/`. The importer now names `municipal` and `business` so a later run reports `blocked_by_robots` with those official URLs instead of ignoring the links. No PDF bytes were fetched. Supreme Court opinion year pages for 2010 through 2016 returned HTTP 404, so no older index counts were recorded. `https://www.legis.ga.gov/` links Georgia Code and the Georgia Constitution to Lexis hosts; those links were not opened and annotations were not scraped. `https://sos.ga.gov/georgia-constitution-revised-2025` and `https://sos.ga.gov/robots.txt` returned HTTP 403, so the Secretary of State constitution compilation was not hashed or stored. These counts are not persisted coverage.

Last production check: 2026-10-08 16:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_ga_regulations --department all --commit` was not run and no corpus rows were written. Discover-only read of the official Rules and Regulations download page used by the importer (department PDF names only; no department PDF downloaded; not stored rules and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | Department PDFs named | Current-through label |
| --- | --- | ---: | ---: | --- | ---: | --- |
| Secretary of State download page | https://rules.sos.ga.gov/Download_pdf.aspx | 200 | 163,972 | `38a9dcc2b062390f55bb1fd51a5b29f7221b77273954032be4c4473b9c9a41d3` | 154 | September 2, 2026 |

Department numbers named on that page: 20, 40, 41, 42, 45, 49, 50, 52, 53, 54, 55, 60, 70, 75, 80, 82, 85, 90, 92, 93, 94, 96, 97, 98, 100, 105, 110, 111, 112, 115, 120, 121, 122, 124, 125, 130, 132, 135, 140, 142, 143, 144, 145, 149, 150, 155, 157, 159, 160, 163, 179, 180, 183, 186, 187, 189, 195, 205, 220, 224, 240, 250, 265, 266, 267, 268, 269, 271, 272, 274, 276, 279, 286, 290, 291, 292, 294, 295, 297, 300, 305, 310, 320, 345, 350, 351, 355, 360, 369, 375, 379, 391, 392, 393, 400, 410, 413, 420, 430, 464, 469, 472, 475, 478, 479, 480, 490, 494, 500, 502, 503, 505, 506, 507, 509, 510, 511, 513, 515, 520, 539, 545, 546, 550, 553, 560, 565, 570, 580, 590, 591, 594, 600, 606, 609, 616, 620, 622, 665, 668, 669, 671, 672, 679, 680, 681, 682, 685, 690, 691, 692, 700, 750, 770. Department 122 is labeled REPEALED. Criminal-adjacent names only, not rule text: 60 Department of Law; 92 Georgia Bureau of Investigation; 97 Department of Juvenile Justice; 105 Georgia Department of Community Supervision; 125 Board of Corrections; 140 Georgia Crime Information Center Council; 144 Georgia Criminal Justice Coordinating Council; 145 Criminal Case Data Exchange Board. `https://rules.sos.ga.gov/robots.txt` returned HTTP 200 (3,440 bytes, SHA-256 `db1aa7d2d2232a53965d633bc3883d16de955bbe0a172ac9609995539f6b4905`). The `*` group allows `/Download_pdf.aspx`, sets crawl-delay 2, and disallows `/gac/*-.*`, `/loadthedata.aspx`, and `/search/`. Per-rule HTML and department PDFs were not fetched. The current-through label is the page's compilation date, not an effective date for any rule. These counts are not persisted coverage.

The Court of Appeals opinion-search URL used by `import_appeals_opinions` (`results_all.php` for 2026-09-01 through 2026-09-07) returned HTTP 405, as did `https://www.gaappeals.gov/rules-1-8/`, `/court-rules/`, and `/robots.txt`. A browser open of `/rules-1-8/` stopped on a human-verification page. No appeals opinion or rule text was read.

Last production check: 2026-10-08 12:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_court_rules --set all` was not run with `--commit` and no corpus rows were written. Discover-only reads of official rule index pages (page bytes and PDF filenames only; PDFs not downloaded; not stored rules and not current-law verification):

| Index | HTTP | Bytes | SHA-256 | PDF links named on the page |
| --- | ---: | ---: | --- | --- |
| https://www.gasupreme.us/rules/ | 200 | 1,592,674 | `9856522213b68148cd6139a4002622da70c7f65771a95e1ffd640b9752e1c3d0` | `SupremeCourtRules_eff-July-2-2026.pdf`, `CHART-WEB-POSTING-July-2-2026.pdf`, `QUICK-REFERENCE-RULES.pdf` |
| https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,686 | `9b6eb00e2a3d9dc49958f7409a7b2544d9ef7297cde643cb423f717e4750504c` | superior 2026-04-09, state 2024-01-18, juvenile 2026-09-03 ADA, probate 2023-06-01, magistrate 2023-04-01, municipal 2024-12-12, statewide business court 2026-06-11 |
| https://www.gaappeals.gov/court-rules/ | 405 | — | — | not read |
| https://www.gaappeals.gov/robots.txt | 405 | — | — | not read |

`https://www.gasupreme.us/robots.txt` returned HTTP 200 (71 bytes, SHA-256 `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196`) and disallows `/wp-content/uploads/`, which is where every PDF above is linked. The importer must not auto-fetch those PDFs. Uniform municipal court rules and statewide business court rules are named on the official page but are not in the importer `RULE_SETS`. The other-rules page also links `https://www.gaappeals.gov/rules-1-8/`; that page was not fetched after the Court of Appeals host returned 405. Filename dates are labels on the index, not verified effective dates. The archive.org `gov.ga.court.rules.odt` checkpoint from the 2022-11 OCGA release was not downloaded. These counts are not persisted coverage.

Last production check: 2026-10-08 11:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. Discover-only reads of the official 2017 and 2018 Supreme Court indexes (importer host, PDF, and first-docket rules; not stored authorities and not current-law verification):

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2017 | https://www.gasupreme.us/2017-opinions/ | 200 | 1,652,091 | 384 | 369 | 0 |
| 2018 | https://www.gasupreme.us/2018-opinions/ | 200 | 1,641,527 | 319 | 316 | 1 |

`discover()` dedupes by URL and would report 369 for 2017. It would refuse the 2018 index until docket `S17A1905` is reviewed: that first-docket token points at more than one PDF. Index SHA-256 checkpoints (page bytes only, not opinion text): 2017 `58151d1549f3f82af864f2e623005ffedaf5f86472f0e636ff6c7b1ab86425d8`; 2018 `700d6ceb867efe20878bac0b5dc02e2f6686e4899595ab2510fc93e27d327dbe`. These counts are not persisted coverage and are not current-law verification. The 2019–2026 index inventories below are unchanged.

Last production check: 2026-10-08 08:20 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_ocga_release --release release86.2022.11 --commit` was not run and no corpus rows were written. Discover-only read of the Public.Resource.Org archive.org metadata for item `gov.ga.ocga.2018`, release `release86.2022.11` (as-of 2022-11, not an effective date and not current-law verification):

| Source | URL | HTTP | Title ODT files | Published bytes | Missing titles 1-53 |
| --- | --- | ---: | ---: | ---: | --- |
| archive.org metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 53 | 38,786,542 | none |

Each title file URL is `https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/gov.ga.ocga.title.NN.odt`. Published SHA-1 values are file checkpoints only. Section text was not downloaded or stored. Lexis annotations were not scraped. The same release also lists, and this run did not download: `gov.ga.ocga.constitution.ga.odt` (1,804,968 bytes, sha1 `b37dfc34a98e2103ea588743a605e12136a08756`), `gov.ga.ocga.constitution.us.odt` (1,719,677, `b53d02725edb45e9ce5c8e1fafa7d60d8566cdfb`), `gov.ga.ocga.index.odt` (6,035,845, `2e7eaf2529d7281864b409bcb1393157cd6e8487`), `gov.ga.court.rules.odt` (3,026,291, `4610a0430d2d6a6dabf67ce569a589bfb0a6a84a`), `gov.ga.court.rules.index.odt` (123,188, `0a499e7d7ff0e89e1af0642489c0082586b1ece6`), and two 6,315-byte AG opinion files with the same sha1 `7f01267e4ee10050ed02458a245a1106fe8793a5`. Later official code and court-rule pages are a separate gap. These counts are not persisted coverage.

| Title | Bytes | Published SHA-1 |
| ---: | ---: | --- |
| 1 | 151,683 | `7f1c767bda5c596515b56638295858453675871c` |
| 2 | 314,047 | `0ba693ed788e23120b116a0a32ba3d162727eee1` |
| 3 | 196,516 | `0791d0938be89e4cb7acc6085073c25891f8c977` |
| 4 | 117,674 | `0f1c093a2659ad9319456d4a2103854f7bc967f6` |
| 5 | 772,483 | `4b53d491dcdad9860999de2b952b1b067d284dee` |
| 6 | 41,120 | `1154cf10ca36e3cba28ecb8d6d6424289256d3cf` |
| 7 | 599,971 | `887b1d46107e1101272a5a6285db8c80dae626df` |
| 8 | 162,817 | `29be57e49fea02c3c26c903fc62f1f025bd27b66` |
| 9 | 2,886,628 | `9f835884da1574eaba955673e5cd5a275e2714f0` |
| 10 | 1,077,445 | `c82147fa77114c5c175b138780adc436bac639e3` |
| 11 | 733,270 | `ffe920deb5c79e4484528f10dcb80b6fa052a2a8` |
| 12 | 832,493 | `cf775cafbd5b5a8a9eb6ac9ba0bf66f31b7e43c8` |
| 13 | 863,613 | `e6abcf43e902cebaaa099b909f980eed015a290a` |
| 14 | 908,409 | `7542c20f973eda7b1a5b0792ddd61bf87c231d8b` |
| 15 | 1,668,827 | `1b2f2df9d0a9967e827a20cc2f229238fedb0aab` |
| 16 | 3,382,207 | `fc0de710946f43d0d1a588651db2fd29ef174c49` |
| 17 | 1,646,017 | `ac725ac4cba54739e00bfee89481ea77767027e0` |
| 18 | 221,792 | `f34e39a1eff7daa387a53eab8587da70db5dbec7` |
| 19 | 936,277 | `e94034ec8905b3e54597054d8661ad1f4b2f396f` |
| 20 | 1,076,479 | `8b2b59c715fd0587f181896cc1c12da7dbdcd60b` |
| 21 | 539,155 | `0464c4187409e6137a03a15cf0b486e6a22d925b` |
| 22 | 172,570 | `786935f74e990c978256e09f141cc3c32d357aac` |
| 23 | 363,503 | `c6b3f48ff22ce7a116055682873ddeeac2674013` |
| 24 | 1,682,900 | `3a660fc0ef3b9609c2dd677af9ea087b5e2ebe5f` |
| 25 | 173,044 | `5cdd2c87f1e52ce44339d294d9f80a378be8fa7c` |
| 26 | 244,609 | `613be9ee4996cb2c637a0c2bb74472a0558b4a22` |
| 27 | 210,894 | `7b8b0e6e3a3755f6d86784f410e369f995352d54` |
| 28 | 76,491 | `7f8d7aac9b9a51f439226a8d5165d11c059e3db7` |
| 29 | 265,989 | `82c0034c04ae9d270b694bd5487b60fe32045a78` |
| 30 | 59,546 | `ff92806e6bf19c19419cbbc01a74ee3eaeea0ab4` |
| 31 | 701,856 | `81d606c33605dd0ab644e25b7acdbed54a6c96c0` |
| 32 | 379,392 | `4201bfd54a342b696b574f819594b7e9c89db2a5` |
| 33 | 1,529,299 | `8f2d85ab54bdb5eb57b8906af3b06609487c3aae` |
| 34 | 1,035,444 | `09200b055c6c3e7026b08d44b387084aaadd6299` |
| 35 | 195,547 | `c3ecaca536a6ed1f00a896baa1952e763777d6f3` |
| 36 | 883,500 | `c4b55ef26589d4bcb160d7071047a671536b3f68` |
| 37 | 273,901 | `f0f89f24ea545f6229f57aef106c10904f9b684d` |
| 38 | 190,871 | `45306c0ac89b64b0cef031d04197fecf487c7a1a` |
| 39 | 22,647 | `a4ae4396aa18c13d345ee253c6ade01208d8d9a5` |
| 40 | 1,260,886 | `eb47c76dee6bc348bca40051a743a4c5ea11dc04` |
| 41 | 85,095 | `8c287467e7c3c9cab1be9e88f9a92c9606358d94` |
| 42 | 471,503 | `0ac38f6b6c3a6167bd0c1f79d0a50815fb6f8c5b` |
| 43 | 1,112,011 | `49203169f6966bac4f5c89943ca513f92f5e4a73` |
| 44 | 1,781,346 | `a84d021831eb522a63cd7675818555dacb14cc0b` |
| 45 | 503,981 | `989687ce07c22ecbb022c3e17216e67449250387` |
| 46 | 637,679 | `b5627c15146a37f97808b6fbd64b9a0bb93df7ec` |
| 47 | 498,817 | `33c91cefeec9624103e138d6a57c7d612f3c0278` |
| 48 | 1,529,531 | `cdd2ce267ea99ffc0e96cc6bd26a1ecaba1a61df` |
| 49 | 302,883 | `01c2f201e1f6e80e215cb39148a1c227e8c3b5c9` |
| 50 | 946,734 | `69a1bdd6d8bbfc1e289a39acd241f3b95b0f3b18` |
| 51 | 1,305,409 | `060c59ea764e9023e0a0873749e10bf7f8841548` |
| 52 | 123,731 | `6f235543ea9286f33f13e871c06fe9b7a6a0c31d` |
| 53 | 636,010 | `ac8ed2dee0046752340ef56b0d993b602bfd3fbf` |

Last production check: 2026-10-06 17:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. Discover-only read of the official 2019 Supreme Court index (importer host, PDF, and first-docket rules; not stored authorities and not current-law verification):

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2019 | https://www.gasupreme.us/2019-opinions/ | 200 | 1,649,016 | 344 | 342 | 0 |

`discover()` dedupes by URL and would report 342. Two PDF URLs each carried two docket labels, but no first-docket token pointed at more than one PDF, so the importer's ambiguous-docket check would not reject this index. These counts are not persisted coverage and are not current-law verification. The 2020–2026 index inventories below are unchanged.

Last production check: 2026-10-06 14:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. Discover-only read of the official 2020 Supreme Court index (importer host, PDF, and first-docket rules; not stored authorities and not current-law verification):

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2020 | https://www.gasupreme.us/2020-opinions/ | 200 | 1,649,294 | 348 | 342 | 0 |

`discover()` dedupes by URL and would report 342. No first-docket token pointed at more than one PDF, so the importer's ambiguous-docket check would not reject this index. These counts are not persisted coverage and are not current-law verification. The 2021–2026 index inventories below are unchanged.

Last production check: 2026-10-06 02:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. Discover-only read of the official 2021 Supreme Court index (importer host, PDF, and first-docket rules; not stored authorities and not current-law verification):

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2021 | https://www.gasupreme.us/2021-opinions/ | 200 | 1,629,741 | 238 | 236 | 0 |

`discover()` keeps unique URLs, so it would report 236 links. No first-docket token pointed at more than one PDF. These counts are not persisted coverage and are not current-law verification. The 2022–2026 index inventories below are unchanged.

Last production check: 2026-10-05 22:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. Discover-only read of the official 2022 Supreme Court index (importer host, PDF, and first-docket rules; not stored authorities and not current-law verification):

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2022 | https://www.gasupreme.us/2022-opinions/ | 200 | 1,627,154 | 221 | 221 | 0 |

`discover()` keeps unique (docket tuple, URL) pairs, so it would report 221 links and 221 PDFs. No first-docket token pointed at more than one PDF. These counts are not persisted coverage and are not current-law verification. The 2023–2026 index inventories below are unchanged.

Last production check: 2026-10-05 17:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. A Court of Appeals opinion-search request for 2026-09-05 through 2026-10-05 returned HTTP 405 with a human-verification page, so no appeals counts were recorded. Discover-only read of the official 2023 Supreme Court index (importer host, PDF, and first-docket rules; not stored authorities and not current-law verification):

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2023 | https://www.gasupreme.us/2023-opinions/ | 200 | 1,627,326 | 219 | 218 | 2 |

`discover()` keeps unique (docket tuple, URL) pairs, so it would report 219 links and 218 PDFs. Two first-docket tokens point at more than one PDF and would need manual review before any import. These counts are not persisted coverage and are not current-law verification. The 2024–2026 index inventories below are unchanged.

Last production check: 2026-10-05 16:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. Discover-only reads of the official annual indexes (importer host, PDF, and first-docket rules; not stored authorities and not current-law verification):

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024 | https://www.gasupreme.us/2024-opinions/ | 200 | 1,630,106 | 238 | 231 | 0 |
| 2026 | https://www.gasupreme.us/2026-opinions/ | 200 | 1,629,113 | 254 | 254 | 0 |

`discover()` dedupes by URL, so it would report 231 for 2024 and 254 for 2026. The 2025 index inventory on the next line is unchanged (247 unique PDF URLs). These counts are not persisted coverage.

# Georgia public ruling coverage

Last production check: 2026-10-05 06:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. A discover-only read of https://www.gasupreme.us/2025-opinions/ returned HTML (1,631,171 bytes, content-type text/html). Using the importer's official-host PDF and first-docket rules: 250 docket-labeled PDF anchors, 247 unique PDF URLs, 0 dockets pointing at more than one PDF. `discover()` dedupes by URL and would report 247. Consolidated PDFs keep only the first docket token in the link text. Those counts are an index inventory, not stored authorities, and are not current-law verification.
This is a coverage ledger, not a claim that all Georgia cases are available.
Last production check: 2026-10-05 01:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were written. A discover-only read of https://www.gasupreme.us/2025-opinions/ returned HTML (about 1.6 MB). Using the importer's official-host PDF and docket rules: 250 docket-labeled PDF anchors, 247 unique PDF URLs, 0 dockets pointing at more than one PDF. `discover()` dedupes by URL and would report 247; consolidated PDFs keep only the first docket token in the link text. Those counts are an index inventory, not stored authorities, and are not current-law verification.
Last production check: 2026-10-03 21:00 UTC. DATABASE_URL was still unset in the automation environment, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were invented.
Last production check: 2026-10-03 08:00 UTC. DATABASE_URL was still unset in the automation environment, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were invented.
Last production check: 2026-10-03 04:00 UTC. DATABASE_URL was still unset in the automation environment, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were invented.
Last production check: 2026-10-02 21:00 UTC. DATABASE_URL was still unset in the automation environment, so `python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit` was not run and no corpus rows were invented.
On 2026-10-02 12:00 UTC the automation environment still had no DATABASE_URL, so the 2025 Supreme Court import was not run and no corpus rows were invented.
`DATABASE_URL` was unset in the automation environment, so
`python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit`
was not run. No corpus was faked and no row counts were invented.
Prior live-database check on 2026-09-28 reported
`legal_sources = 0`, `legal_authorities = 0`, `authority_versions = 0`.
Those stored counts were not rechecked and remain unverified.
Issue 88 is not treated as ingested until a real import records discovered,
attempted, succeeded, and failed counts against a live database.
On 2026-10-02 the automation environment still had no DATABASE_URL, so the 2025 Supreme Court import was not run and no corpus rows were invented.

Guest rights and encounter help already call `POST /public/rights-assistant`
and `GET /public/encounter` without login on web Free research and Android
Know your rights. Private cases and `POST /cases/{id}/motion-screen` stay
login-only. Conflicting PR #38 (verified motion registry) was closed as superseded: main already builds the motion registry from indexed authorities in `motion_screen_service.py` and routes `POST /cases/{id}/motion-screen` through it. The branch was merge-conflicting and was not rebased.
Draft PR #46 (wire verified motion screen) was closed as superseded: main already calls POST /cases/{id}/motion-screen and the branch conflicted with current guest-rights routing. The README still describes a development build because official-source
ingestion is not complete.

| Court / source | Discovered online range | Stored | Gap |
| --- | --- | ---: | --- |
| Supreme Court of Georgia annual opinion pages | 2017–2026 official annual index pages | unverified | 2017–2026 indexes inventoried (2018 has ambiguous docket S17A1905). No opinion PDFs stored. Earlier final reporters and revisions require separate sources. Do not treat the prior zero check as a fresh count. |
| Court of Appeals of Georgia | Official source registered; complete archive not inventoried | unverified | Opinion search, rules-1-8, court-rules index, and robots.txt returned HTTP 405 on 2026-10-08 (search also 405 on 2026-10-05). Browser hit a human-verification page. No opinion or rule text stored. |
| Court rules | Supreme Court rules index and other-court-rules index fetched 2026-10-08; Court of Appeals rules index HTTP 405 | unverified | PDF bodies live under a robots-disallowed uploads path and were not fetched. Municipal and statewide business court PDFs are named but not in importer rule sets. No rule text stored. |
| Rules and Regulations of the State of Georgia | Secretary of State download page, 154 department PDFs named, current-through label September 2, 2026 | unverified | Index only. No department PDF stored. Per-rule HTML is robots-disallowed. Not current-law verification. |
| Georgia trial courts and other public rulings | No unified archive inventoried | unverified | Inventory county and court access, document availability, restrictions and older paper records. Do not dump private trial dockets. |

Official annual index: https://www.gasupreme.us/2026-opinions/

The Supreme Court annual importer can be run in preview batches, for example:

`python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25`

After validating links, metadata, database connectivity, and permissions, an
operator may explicitly add `--commit`. Repeat with increasing `--offset` for
each year. A run must log `discovered`, `attempted`, `succeeded` and `failed`;
compare committed row/version counts in the database. Index pages can change
between batches: audit duplicates, skipped URLs and final copies, and repeat
yearly checks. Do not interpret an HTTP 200 or a preview as persisted coverage.

For documents no longer available from an official source, seek a lawfully
accessible public copy and record its provenance and limitations. Do not
restore sealed, restricted, expunged, or otherwise private material simply
because it was once accessible. Public case histories, docket metadata,
published opinions and full trial-court filings are distinct coverage goals.
The OCGA, including annotations, may be stored (Georgia v. Public.Resource.Org, 2020) with source and release-date provenance; keep annotations separate from statutory text. Do not dump private trial dockets.
Do not present unverified citations as current Georgia law.

