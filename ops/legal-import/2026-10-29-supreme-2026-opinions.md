# 2026-10-29 Supreme Court 2026 opinions index checkpoint

DATABASE_URL was unset, so no opinion PDFs were downloaded and no authority rows were written. Discover-only raw fetch of the annual index succeeded. PDF anchors were counted; robots.txt disallows /wp-content/uploads/ so none were fetched. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,634,293 | `bc6d01dad69af3c0f11c7260496048652f6a85fa54603870cf6fecb16cea3539` | 294 PDF anchors named under /wp-content/uploads/; prior 2026-10-16 hash differed |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The index names additional PDF anchors compared with the 2026-10-16 checkpoint. None were downloaded because of robots.txt. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the public index page only. Full text ingestion remains blocked until DATABASE_URL is set and robots-compliant acquisition is configured. Annotations remain editorial and are not scraped.
