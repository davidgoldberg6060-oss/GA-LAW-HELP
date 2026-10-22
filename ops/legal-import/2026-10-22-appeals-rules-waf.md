# Court of Appeals rules index checkpoint — 2026-10-22

DATABASE_URL is unset. No corpus rows written. No rule text downloaded or stored.

Discover-only raw fetch of the Court of Appeals rules index and robots.txt.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `e2be368fbb10210eb75d1aae58719b8b807b554014383fa5132974bc60c860c8` | AWS WAF captcha; not the rules page |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `67658b579162f625c687fd6b379848ea36e62aaef441cb1de848df0406fe572e` | Same WAF captcha page |

Raw fetch returned the Human Verification / captcha challenge (x-amzn-waf-action: captcha). No rule PDF or HTML text was retrieved. Lexis was not opened. These counts are not persisted coverage.

Gap: Court of Appeals rules remain inaccessible via raw HTTP due to WAF. Prior checkpoints noted the same. Official text is available through the court site in a browser session only.
