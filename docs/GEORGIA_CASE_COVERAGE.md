# Georgia case coverage

Guest rights and encounter help already call `POST /public/rights-assistant`
and `GET /public/encounter` without login on web Free research and Android
Know your rights. Private cases and `POST /cases/{id}/motion-screen` stay
login-only. Draft PR #46 (wire verified motion screen) was closed as superseded: main already calls POST /cases/{id}/motion-screen and the branch conflicted with current guest-rights routing. The README still describes a development build because official-source
ingestion is not complete.

| Court / source | Discovered online range | Stored | Gap |
| --- | --- | ---: | --- |
| Supreme Court of Georgia annual opinion pages | 2017–2026 pages linked from the court's 2026 page | unverified | Index, import, count and check each year; earlier final reporters and revisions require separate sources. Do not treat the prior zero check as a fresh count. |
| Court of Appeals of Georgia | Official source registered; complete archive not inventoried | unverified | Discover official individual opinions and establish dates/counts. |
| Georgia trial courts and other public rulings | No unified archive inventoried | unverified | Inventory county and court access, document availability, restrictions and older paper records. Do not dump private trial dockets. |

Official annual index: https://www.gasupreme.us/2026-opinions/

The Supreme Court annual importer can be run in preview batches, for example:

`python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25`

After validating links, metadata, database connectivity, and permissions, an
operator may explicitly add `--commit`. Repeat with increasing `--offset` for
each year. A run must log `discovered`, `attempted`, `succeeded` and `failed`;
compare committed row/version counts in the database. Index pages can change
between batches: audit duplicates, skipped URLs and final copies, and repeat
yearly checks. Do not interpret an HTTP 200 or a preview as persisted coverage.

## 2026-10-02 automation attempt

`python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit`
was not run. `DATABASE_URL` was not available. No rows were committed and no
coverage count was invented. See `docs/corpus_runs/2026-10-02-supreme-2025-limit-25.md`.
Issue 88 stays open until a real database records committed rows.

For documents no longer available from an official source, seek a lawfully
accessible public copy and record its provenance and limitations. Do not
restore sealed, restricted, expunged, or otherwise private material simply
because it was once accessible. Public case histories, docket metadata,
published opinions and full trial-court filings are distinct coverage goals.
Do not copy the Official Code of Georgia Annotated. Do not dump private trial dockets.
Do not present unverified citations as current Georgia law.
