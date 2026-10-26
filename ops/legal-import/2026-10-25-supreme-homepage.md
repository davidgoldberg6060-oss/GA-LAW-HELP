# 2026-10-25 Supreme Court of Georgia homepage checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the official Supreme Court homepage. Homepage bytes were hashed; no opinion PDFs, rules PDFs, or other documents were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage | https://www.gasupreme.us/ | 200 | 1,599,142 | `10ee5d4427b4e6d9e36b0c84c9d4b15422473a90940ff4641853b16679792fb2` | Official court site; links to opinions indexes, rules, docket search; robots previously checked for uploads |

The homepage provides navigation to forthcoming opinions, annual indexes, rules, and other public materials already inventoried in prior checkpoints. None of the linked documents were fetched in this step. These counts are not persisted coverage. No corpus rows written.

Gap notes: homepage inventory only. Preferred sources for opinions remain the annual indexes and official PDFs when access permits; currency must be verified against the official site. Private case data is never published as authority.
