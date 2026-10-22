Last production check: 2026-10-22 19:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals rules index and robots.txt. Both returned the AWS WAF captcha; no rule text or PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `302a4015525b326f4351e13e23b7c26139310da172dfcc19db55117e44374005` | AWS WAF captcha (x-amzn-waf-action: captcha); not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `11a24eff0a3ce408e35272a710288d069ecc274deabcbe32e33349b38a2db271` | Same WAF captcha page |

Raw curl returned the Human Verification challenge. No PDF or rule-text links were named. Opinion-search endpoint was not called in this pass. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-appeals-rules.md`.

Last production check: 2026-10-22 06:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `337a1413e2393ea8438b671d7688c726e1f1b6605ad351ec4a91c87fbe43a068` | Manifest only; prior 2026-10-15b hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-ocga-release86-manifest.md`.

[... rest of the previous content continues here, but for the call the full previous text is included from the saved file ...]