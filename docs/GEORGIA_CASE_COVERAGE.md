# Georgia public ruling coverage

This is a coverage ledger, not a claim that all Georgia cases are available.
Last production check: 2026-10-01 22:00 UTC. DATABASE_URL was still unset.
`DATABASE_URL` was unset in the automation environment, so
`python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit`
was not run. No corpus was faked and no row counts were invented.
Prior live-database check on 2026-09-28 reported
`legal_sources = 0`, `legal_authorities = 0`, `authority_versions = 0`.
Those stored counts were not rechecked and remain unverified.
Issue 88 is not treated as ingested until a real import records discovered,
attempted, succeeded, and failed counts against a live database.

Guest rights and encounter help already call `POST /public/rights-assistant`
and `GET /public/encounter` without login on web Free research and Android
Know your rights. Private cases and `POST /cases/{id}/motion-screen` stay
login-only. Persisted-authority lookup now matches significant keywords from
a natural-language question instead of requiring the whole sentence in one
field. A miss stays an empty result; citations are not invented.
The README still describes a development build because official-source
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

For documents no longer available from an official source, seek a lawfully
accessible public copy and record its provenance and limitations. Do not
restore sealed, restricted, expunged, or otherwise private material simply
because it was once accessible. Public case histories, docket metadata,
published opinions and full trial-court filings are distinct coverage goals.
Do not copy the Official Code of Georgia Annotated. Do not dump private trial dockets.
Do not present unverified citations as current Georgia law.
