Last production check: 2026-10-08 15:05 UTC. DATABASE_URL was unset, so no importer was run with `--commit` and no corpus rows were written. Discover-only reads of official Supreme Court index pages (page bytes and PDF filenames only; PDFs not downloaded; not stored authorities and not current-law verification):

| Index | HTTP | Bytes | SHA-256 | PDF links named on the page |
| --- | ---: | ---: | --- | --- |
| https://www.gasupreme.us/wp-sitemap-posts-page-1.xml | 200 | 27,234 | `24b1f752b0cbf4d489e879cda5812c52814e220d11694fbc31d83aa56bc3ec1f` | annual opinion pages named only for 2017–2026 |
| https://www.gasupreme.us/2016-opinions/ | 404 | — | — | not an official annual index |
| https://www.gasupreme.us/2015-opinions/ | 404 | — | — | not an official annual index |
| https://www.gasupreme.us/opinions/ | 404 | — | — | not an official annual index |
| https://www.gasupreme.us/forthcoming-opinions/ | 200 | 1,594,143 | `c249fd1a36809b5d52b09721c5c039b67903984c00bbee50cfed739058525b10` | 10 uploads PDFs (not downloaded) |
| https://www.gasupreme.us/rules/former-rules/ | 200 | 1,704,774 | `4430279ade318b0fe3f4f76946f45ce74d1f3b963f80e30c8390ab698343a2f1` | `SupremeCourtRules_eff-July-2-2026.pdf`, `Certificate_of_Timeliness_Template.pdf` |
| https://www.gasupreme.us/other-codes-rules/ | 200 | 1,603,773 | `d0c14c3ee93a6bb129a5a3bd8acc574fa89085a755344257f49b65752e0258fb` | 27 unique uploads PDFs (not downloaded) |
| https://www.legis.ga.gov/laws/code | 200 | 1,492 | `05dd7a574b081f27c023001daa94e1f2f49a3f84151f0c6639ec54d7c691479a` | 0 anchors; JavaScript shell only |

The page sitemap index is https://www.gasupreme.us/wp-sitemap.xml (794 bytes, SHA-256 `b30b41697f88e4ce5d01a18dac07abfba457cb5fb522dc402f0700820290e79f`). It does not name a pre-2017 annual opinion index. Forthcoming-opinion PDF names, all under `/wp-content/uploads/` and not fetched: `s25g1446.pdf` (link text also names S25G1447), `s26a0604.pdf`, `s26a0732.pdf`, `s26a0769.pdf`, `s26a0775.pdf`, `s26a1003.pdf`, `s26a1067.pdf`, `s26a1488.pdf`, `s24z1139.pdf` (link text also names S25Z0722), `s26y0982.pdf`. No first-docket token pointed at more than one PDF. These are not the annual index and are not stored opinions.

`https://www.gasupreme.us/robots.txt` still disallows `/wp-content/uploads/` (71 bytes, SHA-256 `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196`). Former-rules HTML was not extracted. Other-codes PDFs are not in importer `RULE_SETS`: Code of Judicial Conduct, Judicial Qualifications Commission rules, jury composition, legal interpreting, statewide electronic-filing standards, unified appeal, misdemeanor citation rules and forms, and uniform transfer rules. Filename dates are labels on the index, not verified effective dates. https://www.legis.ga.gov/laws/code did not expose OCGA title or section text. Lexis annotations were not scraped. A Court of Appeals opinion-search window for 2026-09-01 through 2026-09-07 and `https://www.gaappeals.gov/robots.txt` again returned HTTP 405, so no appeals counts were recorded. These counts are not persisted coverage.

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
| Supreme Court of Georgia annual opinion pages | 2017–2026 official annual index pages; forthcoming-opinions page names 10 PDFs | unverified | 2017–2026 indexes inventoried (2018 has ambiguous docket S17A1905). Sitemap names no pre-2017 annual index; 2015 and 2016 opinion URLs returned 404. Forthcoming PDFs were not downloaded. No opinion PDFs stored. |
| Court of Appeals of Georgia | Official source registered; complete archive not inventoried | unverified | Opinion search and court-rules index returned HTTP 405 on 2026-10-05 and 2026-10-08 (search window 2026-09-01..2026-09-07 and robots.txt again 405 at 15:05 UTC). Discover official individual opinions and establish dates/counts. |
| Court rules | Supreme Court rules, other-court-rules, former-rules, and other-codes-rules indexes fetched 2026-10-08; Court of Appeals rules index HTTP 405 | unverified | PDF bodies live under a robots-disallowed uploads path and were not fetched. Municipal, statewide business court, judicial-conduct, JQC, and other named codes are not in importer rule sets. Former-rules HTML was not extracted. No rule text stored. |
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
