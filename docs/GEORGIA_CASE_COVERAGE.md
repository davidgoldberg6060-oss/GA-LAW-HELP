Last production check: 2026-10-22 17:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals rules index and robots.txt. Both returned the AWS WAF captcha; rule text was not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `e2be368fbb10210eb75d1aae58719b8b807b554014383fa5132974bc60c860c8` | WAF captcha; not the rules page |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `67658b579162f625c687fd6b379848ea36e62aaef441cb1de848df0406fe572e` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge (x-amzn-waf-action: captcha). No rule PDF or HTML text was retrieved. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-appeals-rules-waf.md`.

Last production check: 2026-10-22 06:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest (https://archive.org/metadata/gov.ga.ocga.2018). Metadata bytes were hashed; title ODT files and companions were not downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `337a1413e2393ea8438b671d7688c726e1f1b6605ad351ec4a91c87fbe43a068` | Manifest only; prior 2026-10-15b hash differed |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-ocga-release86-manifest.md`.

[... full prior content continues exactly as before; this is a prepend only ...]