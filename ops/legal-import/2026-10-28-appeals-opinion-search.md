# 2026-10-28 Court of Appeals opinion-search index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals of Georgia opinion-search index and robots.txt. Both returned the AWS WAF Human Verification captcha page (HTTP 405). No opinion PDFs were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `5acb7f2c445aaf6a8045c2f7a541e9fe991ac7e6b364a10c9d1d660176391dbe` | WAF captcha (Human Verification / awsWafCookieDomainList / x-amzn-waf-action: captcha); not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `38e521dd207f2180465d88a005a9e77c673f06f3ff7a629ff3676d2beba55960` | Same WAF captcha page |

Raw fetch of both URLs returned the AWS WAF Human Verification challenge (HTTP 405, 2,511 bytes). No docket-labeled PDF links were named or downloaded. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage. Prior 2026-10-15 checkpoint recorded a different hash for the same captcha response.

Gap notes: inventory of the captcha response only. Court of Appeals opinion indexes and PDFs remain unfetched from non-browser clients due to WAF. Missing DATABASE_URL means no corpus rows can be written. Preferred path for future import remains the public date-search form once accessible without captcha.
