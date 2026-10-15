Last production check: 2026-10-15 21:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals of Georgia opinion-search index, robots.txt, and rules index. All three returned AWS WAF captcha (HTTP 405, ~2,511 bytes); challenge tokens make the SHA-256 unstable. No opinion PDFs were named or downloaded; not stored opinions and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a4737fa4340600406e95fc008efbcc4da42d4ef3cec62e496602980628193f89` | WAF captcha; not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `44e4f9662079e6ff9aa91cd553537e9b6ce1fe32c3dbead3cd20f5ed861d0a29` | Same WAF captcha |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `677f2f391517ff91d84337ca36c33f1d2ce99624fccf07cb61920f0b49b65e95` | Same WAF captcha; rule PDFs not fetched |

Non-browser clients receive a Human Verification captcha on gaappeals.gov. Date-window opinion search results and Court of Appeals rules remain unfetched by the importer's raw transport. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15-coa-opinion-search-index.md`.

Last production check: 2026-10-15 13:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `25e0c050ac996d061c246bf9b7e495327b03286c4ca0a92031ee876746d8b11b` | Manifest only; prior 2026-10-15 09:00 hash differed (834,799 bytes) |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15b-ocga-release86-manifest.md`. Court of Appeals rules index returned a WAF captcha on raw fetch (HTTP 405); rules pages were not stored. 

[NOTE: Full historical ledger retained in prior commits; this update prepends the 2026-10-15 WAF checkpoint. The complete prior content is preserved by the previous version of this file.]