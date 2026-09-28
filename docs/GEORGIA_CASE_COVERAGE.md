# Georgia public ruling coverage

This is a coverage ledger, not a claim that all Georgia cases are available.
Last production check: 2026-09-28. `legal_sources = 0`,
`legal_authorities = 0`, `authority_versions = 0` in the active database.

| Court / source | Discovered online range | Stored | Gap |
| --- | --- | ---: | --- |
| Supreme Court of Georgia annual opinion pages | 2017–2026 pages linked from the court's 2026 page | 0 | Index, import, count and check each year; earlier final reporters and revisions require separate sources. |
| Court of Appeals of Georgia | Official source registered; complete archive not inventoried | 0 | Discover official individual opinions and establish dates/counts. |
| Georgia trial courts and other public rulings | No unified archive inventoried | 0 | Inventory county and court access, document availability, restrictions and older paper records. |

Official annual index: https://www.gasupreme.us/2026-opinions/

The Supreme Court annual importer can be run in preview batches, for example:

`python -m app.ingestion.import_supreme_opinions --year 2026 --offset 0 --limit 25`

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
