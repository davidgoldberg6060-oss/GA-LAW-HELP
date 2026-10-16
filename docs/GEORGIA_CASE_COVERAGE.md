Last production check: 2026-10-16 18:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `d74ce21fd9b255e9c6ab0a670b2140873ed7806a7f3ab176437fcfd75b2eed96` | Manifest only; prior 2026-10-15 13:02 hash differed (same 834,800 bytes) |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-ocga-manifest.md`. Court of Appeals rules index returned a WAF captcha on raw fetch (HTTP 405); rules pages were not stored.

See previous entries below for full history. (Full ledger restored in this commit from main + this checkpoint.)
