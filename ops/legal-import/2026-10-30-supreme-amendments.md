# Supreme Court rules amendments index checkpoint (2026-10-30)

Fetch date: 2026-10-30 00:01 UTC. DATABASE_URL is unset, so no corpus rows were written. No order PDFs were downloaded. This is not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| amendments index | https://www.gasupreme.us/rules/amendments-to-rules/ | 200 | 1,707,976 | `84a1d398814de77d23e2ec862e96c21959c3bb996fbaae04c7dbda2f99f31ddc` | 309 PDF anchors; robots disallow /wp-content/uploads/; hash differs from 2026-10-16 checkpoint |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The amendments index continues to list order PDFs for Uniform Superior Court Rules, Uniform Juvenile Court Rules, Municipal Court Rules, Statewide Business Court, Supreme Court Rules, and related orders (examples under /wp-content/uploads/). None of those PDFs were fetched because robots.txt disallows `/wp-content/uploads/`. Lexis was not opened or scraped. Court of Appeals pages continue to return AWS WAF captcha on raw fetch from this environment.

Gap notes: inventory of the amendments index only. Individual order PDFs remain unfetched. Missing DATABASE_URL means no corpus rows can be written and no coverage is claimed. Currency and effective-date verification remain unknown pending later official comparison against current compiled rules. This checkpoint does not invent statute or rule text.
