# 2026-10-24 Court of Appeals rules index checkpoint

DATABASE_URL is unset, so no rule PDFs were downloaded and no authority rows were written. Raw fetch of the Court of Appeals rules index and robots.txt returned AWS WAF captcha pages (HTTP 405). No rule text was retrieved. Not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `b9dbe965de786cd6df61da1c05d660500d30b093c777b39b3df92c25fb098ace` | AWS WAF captcha; Human Verification page; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `fb5a596046cc8ba44a19c1a463992d3cfbdc72b9e568b76bfd820072151b8630` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge for both. No PDF anchors or rule text were named. Lexis was not opened. These counts are not persisted coverage. Court of Appeals rules pages continue to be blocked by WAF on raw fetch.
