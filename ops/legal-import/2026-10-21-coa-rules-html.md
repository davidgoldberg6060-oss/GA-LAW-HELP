# Court of Appeals rules HTML sections checkpoint — 2026-10-21

DATABASE_URL was unset. No authority rows were written. No PDFs were downloaded. Lexis was not opened. These counts are not persisted coverage.

## Raw fetch results (curl / automated)

| Source | URL | HTTP | Notes |
| --- | --- | ---: | --- |
| rules index (attempt) | https://www.gaappeals.gov/rules/ | 405 | AWS WAF captcha |
| complete rules PDF | https://www.gaappeals.gov/wp-content/uploads/2026/03/COA-Rules-Complete-Eff-26-March-26.pdf | 405 | AWS WAF captcha; not downloaded |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | AWS WAF captcha |
| rules 1-8 HTML | https://www.gaappeals.gov/rules-1-8/ | 405 | AWS WAF captcha |
| rules 9-10 HTML | https://www.gaappeals.gov/rules-9-10/ | 405 | AWS WAF captcha |
| rules 23-27 HTML | https://www.gaappeals.gov/rules-23-27/ | 405 | AWS WAF captcha |
| rules 28-29 HTML | https://www.gaappeals.gov/rules-28-29/ | 405 | AWS WAF captcha |
| rules 33-36 HTML | https://www.gaappeals.gov/rules-33-36/ | 405 | AWS WAF captcha |
| rule 30 HTML | https://www.gaappeals.gov/rule-30/ | 405 | AWS WAF captcha |

Captcha page size observed: 2,511 bytes. SHA-256 of one captcha response: `18da5cf2f423aea66d3c1225ac9c8168e3bcdc1266df70bb0390659fef2e4bce`.

## Browser-accessible observation (not raw fetch)

Individual section pages (e.g. /rules-1-8/, /rules-9-10/, /rules-23-27/) render the Court of Appeals rules text stating "These rules are effective on March 26, 2026." A Spanish complete-rulebook PDF link and the English complete PDF link are named. No rule text was stored. No current-law verification performed.

Gap notes: automated ingestion is blocked by AWS WAF on the Court of Appeals site. HTML rule sections appear publicly viewable in a browser. Complete PDF is under /wp-content/uploads/ and blocked on raw fetch. Official unannotated OCGA text remains limited to the 2022 Public.Resource.Org / archive.org release86 manifest (previously checkpointed); no newer free unannotated OCGA corpus was located in this pass. Supreme Court of Georgia indexes continue to disallow /wp-content/uploads/ via robots.txt.

No corpus coverage is claimed.
