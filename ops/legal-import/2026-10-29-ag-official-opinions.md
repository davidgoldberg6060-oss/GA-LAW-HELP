# 2026-10-29 Georgia Attorney General official opinions index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the official opinions index at https://law.georgia.gov/opinions/official. Index bytes hashed; individual opinion pages and any PDF targets were not downloaded. Not stored opinion text and not current-law verification. Lexis was not opened.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| official opinions index | https://law.georgia.gov/opinions/official | 200 | 144,468 | `e8991269c051801d1b6a1b25c30b7e9f6676e83049ee1ea0ee13eb352e3d9de5` | 57 relative /opinions/ links observed; no direct .pdf hrefs on the index page itself |

The index lists official AG opinions (examples include recent 2026 items and earlier numbered opinions). No opinion text or PDFs were fetched. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the official opinions index only. Prior 2026-10-10 checkpoint covered the broader /opinions page. Currency and full text remain uningested. A missing DATABASE_URL means no authority rows can be written.
