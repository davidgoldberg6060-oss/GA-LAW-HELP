Last production check: 2026-10-10 15:04 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Secretary of State Rules and Regulations download page (https://rules.sos.ga.gov/Download_pdf.aspx). Page bytes and robots.txt were hashed; department PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| download page | https://rules.sos.ga.gov/Download_pdf.aspx | 200 | 163,973 | `36fca85cfbc0836a8b9afed0a2220c5a68693976115be7b1ac9164f1489e442f` | 154 department PDF labels |
| robots.txt | https://rules.sos.ga.gov/robots.txt | 200 | 3,406 | `9b7272de9a8a6ecdc6d70e11948738271558e464cde15739728fc7f1098c0bca` | Allows general access |

The page names 154 unique departments. Home page notes current through September 17, 2026. None of the PDFs were fetched. Fastcase is named as designated publisher; no XML feeds requested. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-10-sos-rules-download-page.md`.

Last production check: 2026-10-10 11:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `b01dff145e9ceecb8503e6a8a31e29c18de99c7f6148a3f1542baab3675727aa` | Manifest only; prior 2026-10-09 hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53), all with published SHA-1. None were downloaded. Companion files (court rules, constitution compilations, AG stubs, index) were also not downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-10-ocga-release86-manifest.md`.
