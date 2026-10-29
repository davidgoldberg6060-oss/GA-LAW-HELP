# 2026-10-29 Supreme Court 2026 opinions index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia 2026 opinions index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,634,293 | `25fb336e5a23fe7c340d473d906a8066e0ea53e00d2adc10b4451d8e9ad7ccf3` | 294 PDF anchors under /wp-content/uploads/; robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The 2026 opinions index names opinion PDFs under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the public index page only. Preferred bulk opinions remain CourtListener or official PDF downloads once DATABASE_URL is set and robots/terms are respected. Currency unknown until verified.
