# CourtListener Georgia Supreme Court metadata checkpoint (2026-10-18)

DATABASE_URL is unset. No bulk files were downloaded and no authority rows were written.

Discover-only fetch of the CourtListener REST court record for the Supreme Court of Georgia.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court metadata | https://www.courtlistener.com/api/rest/v4/courts/ga/ | 200 | 581 | `8ccd21dd1c4749379ef63a95e57cd5f7f82bc77f7e2bdd3654f7238a70857e0c` | JSON: full_name="Supreme Court of Georgia", start_date=1841-01-01, end_date=null, in_use=true |

This is public metadata only. Bulk opinion data is available from Free Law Project under their terms ("free of known copyright restrictions"); no bulk download was performed. Lexis was not opened. These counts are not persisted coverage.

Gaps remain: Court of Appeals raw pages return AWS WAF captcha; OCGA title ODTs remain inventory only; no production corpus rows because DATABASE_URL is unset.
