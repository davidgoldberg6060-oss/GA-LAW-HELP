# 2026-10-27 OCGA release86 metadata checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of Public.Resource.Org OCGA item metadata (https://archive.org/metadata/gov.ga.ocga.2018). No ODT, RTF, HTML, or statute text files were downloaded. Lexis was not opened. This is not stored statute text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `31287e32dd48012f87cf553e84ad235c1b99b82d8dae72bf8982e2567d20da77` | Manifest only; files_count 3219; item_size ~11.3 GiB; prior 2026-10-25 hash differed (834,800 bytes, fb5e0ff9...) |

Release `release86.2022.11` continues to name title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index). None were downloaded. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the metadata endpoint only. Preferred unannotated bulk source remains this Public.Resource.Org archive; currency of any future import must be verified against newer official sources. Annotations remain editorial and are not scraped. Hash changed from the 2026-10-25 checkpoint; content of individual title files was not inspected.
