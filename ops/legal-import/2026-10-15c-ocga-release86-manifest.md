# OCGA release86.2022.11 manifest checkpoint (2026-10-15c)

Fetch date: 2026-10-15 16:02 UTC. DATABASE_URL is unset. No title ODT files or companions were downloaded. No authority rows were written. This is not stored statute text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,799 | `5da6b1d9fcfe14d71ef326f429e7cf531c679a97940b79bfc08ac8d6992847b4` | Manifest only; prior 2026-10-15 13:02 hash was 834,800 bytes |

Release `release86.2022.11` still names title ODT files (01–53) plus companion files (AG opinions, court rules, constitutions, index). All have published SHA-1. None were downloaded. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the Public.Resource.Org item metadata only. Court of Appeals opinion-search (`https://www.gaappeals.gov/opinion-search/`) and rules pages returned AWS WAF captcha (HTTP 405, Human Verification page) on raw curl and browser fetches the same day; no appeals index text or PDFs stored. Missing DATABASE_URL means no corpus rows can be written.
