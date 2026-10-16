Last production check: 2026-10-16 23:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court former-rules HTML page and robots.txt. Page bytes were hashed; rule text is former/superseded HTML only; current-rules PDF was not downloaded; not stored current rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| former-rules HTML | https://www.gasupreme.us/rules/former-rules/ | 200 | 1,698,294 | `4dc4d51abf7fd05e81e8713eb602ddb174bd5ce79456668aa0fa3d790f3c72f5` | ~121 unique Rule N labels; HTML of former rules |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The page is titled "Former Rules Of The Supreme Court Of Georgia" and notes the rules were amended January 1, 2024. It contains HTML text of prior rules. Two PDF links appear (current rules PDF and a certificate template); neither was fetched because robots.txt disallows `/wp-content/uploads/`. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch (HTTP 405). These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-former-rules.md`.

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

Last production check: 2026-10-09 14:00 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2021 --discover-only --commit` was refused and no corpus rows were written. Discover-only hashed the 2021 annual opinion index and robots.txt (page bytes and docket-labeled PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification). The full prior history continues below the 2026-10-09 14:00 entry in the original ledger.
