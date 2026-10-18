# OCGA release86 manifest checkpoint (2026-10-18)

DATABASE_URL was unset, so no title or companion files were downloaded and no authority rows were written.

Discover-only read of the Public.Resource.Org OCGA release manifest.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `29535250c8aeb5fb73d5cc86133bf03bb6e6543e6f21ca2384511b6668350f21` | Manifest only; prior 2026-10-15 13:02 hash differed |

Release `release86.2022.11` names 53 title ODT files (`gov.ga.ocga.title.01.odt`–`title.53.odt`) plus 7 companions (`gov.ga.ag.2020.opinions.odt`, `gov.ga.ag.2022.opinions.odt`, `gov.ga.court.rules.index.odt`, `gov.ga.court.rules.odt`, `gov.ga.ocga.constitution.ga.odt`, `gov.ga.ocga.constitution.us.odt`, `gov.ga.ocga.index.odt`), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch.
