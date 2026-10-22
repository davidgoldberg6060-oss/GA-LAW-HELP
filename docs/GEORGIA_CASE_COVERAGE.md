Last production check: 2026-10-22 15:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia court-rules index and robots.txt. Both returned the AWS WAF captcha (HTTP 405); rule pages were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `4bfb1e66e92ed2f3f25a970503f724424fc0e63a3d0104ac8223612695833bb8` | WAF captcha; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `04b9aa997bbfd23df03898e4336ae180596c8b95d24cf57b253f6808bf532282` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No rule page links were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-appeals-court-rules.md`.

Last production check: 2026-10-22 06:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `337a1413e2393ea8438b671d7688c726e1f1b6605ad351ec4a91c87fbe43a068` | Manifest only; prior 2026-10-15b hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-ocga-release86-manifest.md`.

