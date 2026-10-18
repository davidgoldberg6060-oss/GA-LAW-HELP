Last production check: 2026-10-18 00:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `29535250c8aeb5fb73d5cc86133bf03bb6e6543e6f21ca2384511b6668350f21` | Manifest only; prior 2026-10-15 13:02 hash differed |

Release `release86.2022.11` names 53 title ODT files plus 7 companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-18-ocga-release86-manifest.md`. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch.

