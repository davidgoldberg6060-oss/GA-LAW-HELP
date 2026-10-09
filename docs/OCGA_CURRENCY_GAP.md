# OCGA currency gap

Last check: 2026-10-09. DATABASE_URL was unset, so no authority rows were written.

The General Assembly page labeled Georgia Code links to `http://www.lexisnexis.com/hottopics/gacode`. That URL was not opened. Do not scrape Lexis annotations or publisher text.

`https://www.legis.ga.gov/laws` returned a 1,492-byte application shell (SHA-256 `05dd7a574b081f27c023001daa94e1f2f49a3f84151f0c6639ec54d7c691479a`). The client route then showed page-not-found. That response is not unannotated OCGA text.

The signed-by-governor search for the 2025-2026 Regular Session rendered "Showing Results 1-20 of 742". That label is not a stored act count, and it is not proof that each act amends the OCGA. No bill text was downloaded. `release86.2022.11` remains an as-of date, not current-law verification.

Supreme Court annual indexes for 2015 and 2016 returned HTTP 404. The importer still starts at 2017. Court of Appeals `robots.txt` and `/opinions/` returned HTTP 405, so no appeals opinion index was recorded.

These notes are not persisted coverage. Educational use only; not legal advice; do not fabricate citations.
