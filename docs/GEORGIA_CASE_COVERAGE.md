Last production check: 2026-10-22 22:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia home page and robots.txt. Both returned the AWS WAF captcha; opinion PDFs were not downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| home page | https://www.gaappeals.gov/ | 405 | 2,511 | `8d305a4174fa42014358f1fec3a2357df8eea76c5ac17f1b70cac00f813dfb25` | WAF captcha; not the court home content |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `3a7222e0a11de818045cb151f7d944b507eabccba51bcaa16e3f9a5c4c07cdb7` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No docket-labeled PDF links were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-appeals-home.md`. Court of Appeals opinion indexes remain blocked by WAF on raw fetch.

Last production check: 2026-10-22 06:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `337a1413e2393ea8438b671d7688c726e1f1b6605ad351ec4a91c87fbe43a068` | Manifest only; prior 2026-10-15b hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-ocga-release86-manifest.md`.
