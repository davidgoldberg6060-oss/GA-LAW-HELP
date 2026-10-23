Last production check: 2026-10-23 11:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `7a1507a3750cedcf2db9e8fa9a3172f79b31179c90a1fba15560d908a2acc266` | Manifest only; prior 2026-10-22 hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-ocga-release86-manifest-refresh.md`.

Last production check: 2026-10-23 09:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Judicial Council / Administrative Office of the Courts Supreme Court and related rules index (https://georgiacourts.gov/georgia-supreme-court-rules/). Index bytes were hashed; PDF anchors counted; gasupreme.us robots.txt disallows /wp-content/uploads/ so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `8fc27ecebaa34124a3ed2169192c825400992959bbb8ea00653afd47c2287cb3` | 28 PDF anchors, all under www.gasupreme.us/wp-content/uploads/; robots on gasupreme.us disallow /wp-content/uploads/ |

The index names 28 unique PDF links (Supreme Court Rules eff. 1.1.24, Uniform Superior/State/Juvenile/Probate/Magistrate/Municipal Court Rules of various dates, Statewide Business Court, Unified Appeal, Uniform Misdemeanor Citation, Transfer Rule, Interpreting, Jury Composition, JQC Rules, and others). None were fetched. More recent versions exist on the gasupreme.us other-court-rules index. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-georgiacourts-rules-index.md`.

Last production check: 2026-10-23 08:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org scanned OCGA volumes item metadata (https://archive.org/metadata/gov.ga.ocga.2024). Metadata bytes were hashed; volume PDFs, OCR text, and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2024 | 200 | 240,237 | `4959077dac3f3b833def013fcac71015266933fd6466b4ff3b7777aef91a0b45` | Manifest only; 629 files; 52 PDF volumes of mixed years (2007–2024) |

The item lists 52 PDF volumes (examples C01 US Const (V1) 2007.pdf, T07-T08 (V5) 2024.pdf) plus derived Text/DjVu/hOCR/EPUB formats. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-ocga-2024-scanned.md`. This source is not preferred for import (OCR, no supplements).

Last production check: 2026-10-22 23:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Secretary of State Georgia Constitution revised 2025 page and robots.txt. Both returned Cloudflare challenge pages; constitution text was not retrieved; not stored constitution text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| constitution page | https://sos.ga.gov/georgia-constitution-revised-2025 | 403 | 5,446 | `74e34e06f812fad7ec10f63cebc3c17cd2657ab7f0d6f6cdad84c7b1aa623175` | Cloudflare challenge page; not constitution text |
| robots.txt | https://sos.ga.gov/robots.txt | 403 | 5,356 | `15499df10a6a491e52bdf5833fc04963ab43e723c03819ba49a8ebf8fb84645a` | Same Cloudflare challenge |

Raw fetch returned the Cloudflare "Just a moment..." security verification page for both. No constitution text was retrieved. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-sos-constitution.md`.

Last production check: 2026-10-22 06:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `337a1413e2393ea8438b671d7688c726e1f1b6605ad351ec4a91c87fbe43a068` | Manifest only; prior 2026-10-15b hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-ocga-release86-manifest.md`.
