# 2026-10-29 Court of Appeals opinion-search and rules WAF checkpoint

Fetch date: 2026-10-29 04:01 UTC. DATABASE_URL was unset, so no opinion or rule PDFs were downloaded and no authority rows were written. This is not stored opinion or rule text and not current-law verification.

Raw fetches of the Court of Appeals of Georgia opinion-search index, rules index, homepage, and robots.txt all returned the AWS WAF Human Verification captcha page (HTTP 405, x-amzn-waf-action: captcha). No PDF anchors were named or downloaded. Lexis was not opened.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a88cb53115405897ca2e525d62b840a6c00a33f0dc34e87e5e5e0278414e5972` | WAF captcha; prior 2026-10-15 hash differed |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `7985a13242ce0f755e3a27f2d65c41d1a7f3afa60be4b23fd9eabd143971d3cb` | WAF captcha |
| homepage | https://www.gaappeals.gov/ | 405 | 2,511 | `83417105c4d74270a73c4354b4aa65080b70ed8490a2876a5f631644b5b5a5e8` | WAF captcha |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `d9d5a87109f7094f3db7761908780142e334a3d7c2c61495e91c28f6fe975c25` | WAF captcha; prior hash differed |

These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the captcha responses only. Court of Appeals opinion indexes, rules pages, and PDFs remain unfetched from non-browser clients due to persistent WAF. Missing DATABASE_URL means no corpus rows can be written. Companion Supreme Court and other-court rules indexes remain available on gasupreme.us (prior checkpoints). Preferred bulk unannotated OCGA source remains Public.Resource.Org archive.org. Annotations remain editorial and are not scraped.
