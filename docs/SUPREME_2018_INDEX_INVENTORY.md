# 2018 Supreme Court of Georgia index inventory

Last production check: 2026-10-08 06:00 UTC. `DATABASE_URL` was unset, so `python -m backend.app.ingestion.import_supreme_opinions --year 2018 --limit 25 --commit` was not run and no corpus rows were written.

Discover-only read of the official index https://www.gasupreme.us/2018-opinions/ using the importer host, PDF, and first-docket rules in `backend/app/ingestion/supreme_listing.py`. This is not stored authorities and not current-law verification.

| Year | Index | HTTP | Bytes | Docket-labeled PDF anchors | Unique PDF URLs | Dockets with more than one PDF |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2018 | https://www.gasupreme.us/2018-opinions/ | 200 | 1,641,527 | 319 | 316 | 1 |

`discover()` keeps unique (docket tuple, URL) pairs, so it would report 317 links and 316 PDFs. One first-docket token points at more than one PDF and would need manual review before any import. Do not treat these counts as persisted coverage.

No Lexis annotations and no section text were copied. Official unannotated code remains the Code Revision Commission index, not this opinion page.
