# 2026-10-29 Georgia Courts rules index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Georgia Courts Supreme Court rules index (https://georgiacourts.gov/georgia-supreme-court-rules/). Index bytes hashed; PDF anchors counted; uploads are robots-disallowed on gasupreme.us so no rule PDFs were downloaded; not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `3fa91dbbbf410191d3a9b02c2949582944d9fd051f4e6f575a6a418bad10ca43` | 28 PDF anchors under gasupreme.us/wp-content/uploads/; also links to https://www.gaappeals.us/rules-1-8/ (legacy) and gasupreme.us/rules/; prior 2026-10-23 hash differed |
| robots.txt (gasupreme.us) | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The index names current Supreme Court Rules PDFs, charts, uniform court rules, and a Court of Appeals rules link. robots.txt on gasupreme.us disallows /wp-content/uploads/, so none of the PDFs were fetched. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the index page only. Court of Appeals rules PDFs remain behind the same robots-disallowed path or the legacy gaappeals.us domain. Preferred bulk sources for unannotated statutes remain Public.Resource.Org; annotations are not scraped.
