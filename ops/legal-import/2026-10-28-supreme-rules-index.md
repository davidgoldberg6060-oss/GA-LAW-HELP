# 2026-10-28 Supreme Court rules index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index (https://www.gasupreme.us/rules/). Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,174 | `99ca258b7794b9181d63dd3c2b056a867be72edcee4d77aad0e05b7a19027f77` | 3 PDF anchors under /wp-content/uploads/ (Supreme Court Rules eff. July 2, 2026; chart; quick-reference); robots disallow; prior 2026-10-23 hash differed |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The rules index names the Supreme Court Rules PDF effective July 2, 2026, a chart, and a quick-reference PDF. robots.txt disallows /wp-content/uploads/, so none were fetched. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the public index page only. Rule text remains uningested. Currency of any future import must be verified against the official source. No annotations scraped.
