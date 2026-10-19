Last production check: 2026-10-19 08:05 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia oral argument calendar index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no calendar PDF was downloaded; not stored argument schedule and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| oral argument calendar | https://www.gasupreme.us/calendar-list/ | 200 | 1,606,851 | `1eccfd2c1f8e67dd66a15e5754d26671a4905da3b7499d092c484f7e6a77b1c2` | 1 PDF anchor (2026-Calendar.pdf under /wp-content/uploads/); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The calendar index names one PDF link (https://www.gasupreme.us/wp-content/uploads/2026/05/2026-Calendar.pdf) for the 2026 oral argument calendar (potential dates, admissions, holidays; subject to change). It points under /wp-content/uploads/. robots.txt disallows that path, so the PDF was not fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-19-supreme-calendar.md`.

PLACEHOLDER_FULL_HISTORY