# 2026-10-28 AG official opinions index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the official category index (https://law.georgia.gov/opinions/official). No opinion PDFs were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| official opinions index (page 0) | https://law.georgia.gov/opinions/official | 200 | 144,468 | `ef6953aefe1f8ee40898c8e538eeb83b98d6dba230e6144c8a4a99813d9fcf40` | Index labels only; 47 unique citation paths named; 4 PDF download links named (including one DO-NOT-SHARE) |
| robots.txt | https://law.georgia.gov/robots.txt | 200 | 1,677 | `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b` | Allows /opinions |

The official index page names 47 citation labels (examples include 2010-6 through 2026-2). Four document download links appeared; one is marked UNPUBLISHED / DO-NOT-SHARE. None of the PDFs were fetched. Pagination of the official category and other category indexes were not walked in this checkpoint. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the official category index page 0 only. Opinion text remains unfetched. Preferred bulk unannotated statute source remains Public.Resource.Org; AG opinions are a separate public source. Missing DATABASE_URL means no authority rows can be written.
