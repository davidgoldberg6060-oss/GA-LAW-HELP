# Court of Appeals of Georgia — discover-only WAF checkpoint

Fetch date: 2026-10-13 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. No PDFs or opinion text were downloaded.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a195ed7ea0dfda81c166f757812ca32ee6762d93d0b819557858da78d3ff1457` | WAF captcha (Human Verification) |
| rules page | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `38780eb0e54753ee26ada35cb503c13a3fc77b24a3e3d93e4cd6d7137845db3f` | WAF captcha (Human Verification) |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `f6df69099b60293e8d5796a3aae4bef9fa6a1f0a77c0cac449710c23857971f2` | WAF captcha (Human Verification) |

All three URLs returned HTTP 405 with `x-amzn-waf-action: captcha` and a 2,511-byte HTML page titled "Human Verification". No index labels, PDF links, or rule text were obtained. The date-search endpoint was not requested. Lexis was not opened. These are blocked checkpoints, not stored opinions or rules, and not current-law verification. No corpus rows written.

Gap notes: Court of Appeals public indexes remain blocked by WAF from this environment. Prior coverage notes the same captcha on the opinion-search page. Companion rules pages also blocked. Missing DATABASE_URL means no authority rows can be written.
