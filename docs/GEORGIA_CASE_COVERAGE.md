Last production check: 2026-10-16 21:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `88c4015f72716f22e6712d3ed7170d7033ae3b85ef053be943f29f510ce89a4d` | Manifest only; prior 2026-10-15 13:02 hash differed (same byte count) |

Release `release86.2022.11` continues to name 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16b-ocga-release86-manifest.md`. Court of Appeals rules and opinion-search indexes continue to return AWS WAF captcha on raw fetch. SOS constitution page returned Cloudflare challenge.

