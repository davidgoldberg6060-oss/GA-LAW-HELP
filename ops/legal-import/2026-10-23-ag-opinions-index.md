# 2026-10-23 Georgia Attorney General opinions index checkpoint

DATABASE_URL was unset. Discover-only fetch of the Georgia Attorney General official opinions index (https://law.georgia.gov/opinions). Index bytes were hashed; opinion PDFs or documents were not downloaded. Not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinions index | https://law.georgia.gov/opinions | 200 | 146,784 | `84e54cf4281caed04a05fe15df5940bad76a68531955e98e46a77bd966a9f0e1` | Index labels only; prior 2026-10-10 hash differed (146,783 bytes) |
| robots.txt | https://law.georgia.gov/robots.txt | 200 | 1,677 | `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b` | Allows /opinions |

The index names citation-style links (examples 2013-2 through later years and U-prefixed) and category indexes (official, unofficial, obsolete-and-modified). Document download links were present in prior checks; none were fetched in this pass. Category indexes and pagination were not walked. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
