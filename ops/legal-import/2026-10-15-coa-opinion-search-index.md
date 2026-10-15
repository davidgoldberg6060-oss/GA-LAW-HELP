# Court of Appeals opinion-search index checkpoint (2026-10-15)

Fetch date: 2026-10-15 ~21:01 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinions and not current-law verification.

Raw non-browser fetch of the public opinion-search page, robots.txt, and rules index (allowed by prior robots notes, but blocked by WAF):

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a4737fa4340600406e95fc008efbcc4da42d4ef3cec62e496602980628193f89` | AWS WAF captcha (Human Verification); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `44e4f9662079e6ff9aa91cd553537e9b6ce1fe32c3dbead3cd20f5ed861d0a29` | Same WAF captcha; prior non-WAF robots text is known but this fetch did not retrieve it |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `677f2f391517ff91d84337ca36c33f1d2ce99624fccf07cb61920f0b49b65e95` | Same WAF captcha; rule PDFs not named or downloaded |

Challenge tokens inside the captcha HTML differ across requests, so the SHA-256 is not stable. No efast.gaappeals.gov PDF links were followed. Lexis was not opened. These counts are not persisted coverage.

Gap notes: non-browser clients receive an AWS WAF captcha on gaappeals.gov. Opinion-search date-window results and Court of Appeals rules remain unfetched by the importer's raw transport. Missing DATABASE_URL means no corpus rows can be written. Prior checkpoints already recorded the same WAF behavior for rules indexes.
