# 2026-10-21 SOS Rules and Regulations download-page checkpoint

DATABASE_URL was unset. No regulation PDFs were downloaded and no authority rows were written.

Discover-only fetch of https://rules.sos.ga.gov/Download_pdf.aspx (HTTP 200, 164,602 bytes, SHA-256 73cb296a2b006af0c053b8503a659e8db963fb5d04ed16a62ee45200b652a09c).

The page names 154 unique Department PDF labels via query-parameter style links (examples: Department 560 RULES OF DEPARTMENT OF REVENUE; Department 111 RULES OF DEPARTMENT OF COMMUNITY HEALTH) plus bulletin labels. None of those files were fetched.

robots.txt: HTTP 200, 3,672 bytes, SHA-256 82f2490c3166cbed7147c472d96ba3e84f31958601ce7ffc3f90b26677a37874. Contains bot-specific Disallow rules; prior 2026-10-16 hash differed.

Court of Appeals rules pages (https://www.gaappeals.gov/rules/ and /rules-1-8/) returned AWS WAF captcha (HTTP 405) on raw fetch. Lexis was not opened.

These counts are not persisted coverage and not current-law verification.
