# 2026-10-29 Court of Appeals (gactapp) CourtListener metadata checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Free Law Project CourtListener REST API court record for the Court of Appeals of Georgia. No opinion text, PDFs, or bulk files were downloaded. Official gaappeals.gov opinion-search remains behind AWS WAF for non-browser clients. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court metadata | https://www.courtlistener.com/api/rest/v4/courts/gactapp/ | 200 | 607 | `5fb097c0a36c7f9cc938329afe196f6658dba2f3d05aca587343709e9abe38be` | id=gactapp; short_name=Court of Appeals of Georgia; has_opinion_scraper=true; start_date=1906-11-06; jurisdiction=SA; in_use=true |

Public search listing on CourtListener for court=gactapp reports approximately 130,000 opinions (as of fetch). Official site https://www.gaappeals.gov/opinion-search/ continues to return WAF captcha (HTTP 405) to raw clients; no bulk index or PDF list was obtained from it. CourtListener bulk data is free of known copyright restrictions; opinions themselves are government edicts. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the public API court record and search-listing size only. Preferred bulk path for appellate opinions remains CourtListener (courts gactapp / ga). Official court site indexes stay inaccessible to automated non-browser fetches due to WAF. Currency and completeness of any future import must be verified against official sources; sealed/restricted/unpublished opinions are excluded by design. Missing DATABASE_URL means no authority rows can be written.
