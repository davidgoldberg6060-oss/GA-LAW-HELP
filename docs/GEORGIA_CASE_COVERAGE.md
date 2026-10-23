Last production check: 2026-10-23 10:05 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `232c78915056a95d290d6945f1e3614bbdbf46c673f7eea2ab616ebdb16283f3` | Manifest only; prior 2026-10-22 hash differed (834,799 bytes) |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-ocga-release86-manifest.md`.

Last production check: 2026-10-23 09:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Judicial Council / Administrative Office of the Courts Supreme Court and related rules index (https://georgiacourts.gov/georgia-supreme-court-rules/). Index bytes were hashed; PDF anchors counted; gasupreme.us robots.txt disallows /wp-content/uploads/ so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `8fc27ecebaa34124a3ed2169192c825400992959bbb8ea00653afd47c2287cb3` | 28 PDF anchors, all under www.gasupreme.us/wp-content/uploads/; robots on gasupreme.us disallow /wp-content/uploads/ |

The index names 28 unique PDF links (Supreme Court Rules eff. 1.1.24, Uniform Superior/State/Juvenile/Probate/Magistrate/Municipal Court Rules of various dates, Statewide Business Court, Unified Appeal, Uniform Misdemeanor Citation, Transfer Rule, Interpreting, Jury Composition, JQC Rules, and others). None were fetched. More recent versions exist on the gasupreme.us other-court-rules index. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-georgiacourts-rules-index.md`.

