# Court of Appeals of Georgia opinion-search index — discover-only checkpoint

Fetch date: 2026-10-15 (UTC). DATABASE_URL was unset, so no opinion PDFs were downloaded and no corpus rows were written.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search page | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `c462a7d492ff4308ae67765d50e98010073b743fc5e161cce4c00f01daf52c88` | AWS WAF Human Verification captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `b2f53e10610539a262d87d033871c5939cd5d239781e671077289a950791c12f` | AWS WAF Human Verification captcha |

Both URLs returned the AWS WAF captcha challenge page (HTTP 405, `x-amzn-waf-action: captcha`). The real opinion-search index and robots.txt were not retrieved. No date-window search was performed. No efast PDFs were named or downloaded. Lexis was not opened. These counts are not persisted coverage.

Gap notes: WAF captcha blocks automated index read. Prior notes already recorded WAF on the opinion search. No corpus rows written. Missing DATABASE_URL means no authority rows can be written.
