# Court of Appeals of Georgia rules inventory checkpoint (2026-10-15c)

Fetch date: 2026-10-15 (UTC). DATABASE_URL is unset. No rule text or PDFs were downloaded or stored. No authority rows were written. This is not stored court-rule text and not current-law verification.

Raw HTTP clients receive an AWS WAF captcha challenge (HTTP 405, ~2511 bytes HTML) for both the rules index paths and the complete rulebook PDF. Browser-rendered pages are accessible and name the rules effective March 26, 2026.

| Source | URL | Notes |
| --- | --- | --- |
| rules group pages (examples) | https://www.gaappeals.gov/rules-1-8/ and similar (/rules-11-15/, /rules-23-27/, /rules-33-36/, /rule-30/, /rule-40/) | Browser-accessible HTML; effective date labeled March 26, 2026; full text not stored |
| complete English rulebook PDF (named) | https://www.gaappeals.gov/wp-content/uploads/2026/03/COA-Rules-Complete-Eff-26-March-26.pdf | Named on site; raw fetch blocked by WAF captcha; not downloaded |
| Spanish complete rulebook PDF (named) | https://www.gaappeals.gov/wp-content/uploads/2026/03/ES-MX.completerulebook-32126-Final-1.pdf | Named on /rules-1-8/; not downloaded |
| opinion search | https://www.gaappeals.gov/opinion-search/ | Dynamic docket/date search form; no static annual opinion index pages like Supreme Court |
| robots.txt | https://www.gaappeals.gov/robots.txt | Disallows /wp-admin/ only; raw fetch also hit captcha |

Gap notes: Court of Appeals rules are published as grouped HTML pages plus a complete PDF effective March 26, 2026. No static yearly opinion indexes exist on the public site (use opinion/docket search). WAF blocks non-browser clients from raw fetches. Lexis was not opened. These are inventory labels only, not persisted coverage. Missing DATABASE_URL means no corpus rows can be written.
