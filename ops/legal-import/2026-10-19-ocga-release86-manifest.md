# OCGA release86 manifest and Court of Appeals rules checkpoint (2026-10-19)

Fetch date: 2026-10-19 12:02 UTC. DATABASE_URL is unset. No title ODT files, companion files, or rule pages were downloaded. No authority rows were written. This is not stored statute or rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `7a047293f105af680f396c22235faca706a474e1be37ab5a2e545a1ac45a9b50` | Manifest only; prior 2026-10-15 13:02 hash differed |
| Court of Appeals rules page | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `e6d9e0d7075bab113b04a6bc7b60742a6c40d281884938c81c8f5e3d43be7564` | WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `d0fc39bc760afead628ac9ecc5e15715d6e83e7ed0e85af143bfaf935e7eb380` | Same WAF captcha page |

Release `release86.2022.11` names 53 title ODT files (01–53) plus companions (AG opinions, court rules, constitutions, index), all with published SHA-1. None of those files were fetched. Lexis was not opened. Raw fetch of the Court of Appeals rules page and robots.txt returned the AWS WAF captcha (HTTP 405). These counts are not persisted coverage.

Gap notes: inventory of the OCGA release manifest labels and hashes only. Statute text remains unfetched. Court of Appeals rules remain blocked by WAF on raw fetch. Missing DATABASE_URL means no corpus rows can be written. Currency of the 2022.11 release is unknown relative to later legislative sessions.
