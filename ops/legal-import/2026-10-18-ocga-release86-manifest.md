# 2026-10-18 OCGA release86 manifest checkpoint

DATABASE_URL was unset, so no title or companion files were downloaded and no authority rows were written.

Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018).

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `6fb4c7afed1cc25c41146c82b42ddaa6d469b416b875f99273cb02a1605aeca3` | Manifest only; prior 2026-10-16 hash differed (same byte count) |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage.

Court of Appeals rules index returned AWS WAF captcha on raw fetch (HTTP 405).
