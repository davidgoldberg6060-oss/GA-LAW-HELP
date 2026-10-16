# Georgia Official-Source Inventory Summary

**Status as of 2026-10-16:** DATABASE_URL is unset. No corpus rows have been written. No coverage is claimed. All entries below are discover-only inventory checkpoints (index pages, manifests, or robots.txt). No statute text, opinion PDFs, or rule text has been stored as authority. Lexis annotations were not opened.

## Inventory Status

| Category | Source | Last Checkpoint | Status | Gaps |
| --- | --- | --- | --- | --- |
| OCGA unannotated | Public.Resource.Org release86.2022.11 manifest (archive.org/metadata/gov.ga.ocga.2018) | 2026-10-15 | Manifest hashed; 53 title ODTs + companions named with SHA-1 | No title files downloaded; not current-law verification; official free unannotated text on legis.ga.gov is SPA/Lexis-linked |
| Court rules | gasupreme.us/other-court-rules/ and /rules/ | 2026-10-13 | Index pages hashed; Uniform/other and Supreme rules PDF labels named | robots.txt disallows /wp-content/uploads/; no PDFs fetched; Court of Appeals rules hit WAF |
| Court rules | rules.sos.ga.gov/Download_pdf.aspx | 2026-10-16 | Download page hashed; ~154 department PDF labels named | No department PDFs downloaded |
| Appellate opinions | gasupreme.us yearly indexes (2017–2026) | 2026-10-16 (2026) | Index pages hashed; docket-labeled PDF anchors counted | robots.txt disallows uploads; no opinion PDFs fetched; some years have parse edge cases |
| Appellate opinions | gaappeals.gov/opinion-search/ | 2026-10-15 | WAF captcha (HTTP 405) | No index or PDFs accessible via raw fetch |
| AG opinions | law.georgia.gov/opinions | 2026-10-10 | Index hashed; ~46 citation labels named | No opinion documents downloaded |
| Session summaries | legis.ga.gov/general-statutes | 2026-10-10 | SPA shell hashed; 21 annual summary PDF labels named | PDFs not downloaded; not section text |

## Provenance Requirements for Future Ingestion

When DATABASE_URL is set and ingestion is authorized:
- Record citation, source URL, source-byte hash, fetch date, and gap notes for every authority.
- Treat currency as unknown unless an official source states otherwise.
- Idempotent imports; do not invent text.
- Exclude sealed/juvenile/expunged/restricted/private records.
- Guest path remains educational only; no fabricated citations.

## Next Safe Steps (no secrets required)

- Continue discover-only checkpoints for remaining public indexes (e.g., additional SOS department pages, historical constitutions if publicly fetchable without captcha).
- Improve keyword/full-text retrieval tests and empty-coverage messaging (already partially addressed).
- Keep guest AI Help on `/public/rights-assistant` only.

Full chronological ledger: `docs/GEORGIA_CASE_COVERAGE.md`. Individual checkpoints: `ops/legal-import/`.
