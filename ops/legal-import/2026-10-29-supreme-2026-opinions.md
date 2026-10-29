# 2026-10-29 Supreme Court 2026 opinions index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Supreme Court of Georgia 2026 opinions index (https://www.gasupreme.us/2026-opinions/). Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,634,293 | `6deb0bb0f6a033316519479baf1c1721113db079bc80f6187f14521ff0b5c726` | 294 PDF anchors under /wp-content/uploads/; robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The 2026 opinions index names 294 PDF anchors (sample docket numbers include s26a0636, s26a0674). robots.txt disallows /wp-content/uploads/, so none were fetched. Prior 2026-10-16 checkpoint recorded 283 PDF anchors and a different byte size/hash. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the annual index page only. Opinion PDFs remain inaccessible under robots.txt. Currency and full text must be verified against official sources when DATABASE_URL is available for a controlled import. Annotations remain editorial and are not scraped.
