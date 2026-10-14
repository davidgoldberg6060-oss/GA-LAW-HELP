# Court of Appeals rules index — discover-only checkpoint

Fetch date: 2026-10-14 (UTC). DATABASE_URL was unset, so no rule pages or PDF files were downloaded as corpus material and no corpus rows were written.

The official Court Rules index at https://www.gaappeals.gov/court-rules/ names 21 rule-section pages. Direct automated fetches of the index and robots.txt returned HTTP 405 with an AWS WAF captcha challenge (x-amzn-waf-action: captcha), so raw page-byte hashes could not be recorded in this environment. The rendered index labels below were observed via a browse tool. robots.txt (observed content) disallows only `/wp-admin/` and allows `/wp-admin/admin-ajax.php`; it lists a sitemap. No PDFs were fetched. Lexis was not opened. These labels are not stored rule text and not current-law verification. These counts are not persisted coverage.

## Rule-section pages named on the index (not downloaded)

| Label | URL |
| --- | --- |
| Rules 1-8: General | https://www.gaappeals.gov/rules-1-8/ |
| Rules 9-10: Attorneys | https://www.gaappeals.gov/rules-9-10/ |
| Rules 11-15: Dockets and Calendars | https://www.gaappeals.gov/rules-11-15/ |
| Rule 16: Extension of Time for Filing | https://www.gaappeals.gov/rule-16/ |
| Rules 17-21: Records and Transcripts | https://www.gaappeals.gov/rules-17-21/ |
| Rule 22 Reserved | https://www.gaappeals.gov/rule-22/ |
| Rules 23-27 Briefs | https://www.gaappeals.gov/rules-23-27/ |
| Rules 28-29 Argument | https://www.gaappeals.gov/rules-28-29/ |
| Rule 30 Applications For Interlocutory Appeal | https://www.gaappeals.gov/rule-30/ |
| Rule 31 Applications For Discretionary Appeal | https://www.gaappeals.gov/rule-31/ |
| Rule 32 Transfer Of Applications | https://www.gaappeals.gov/rule-32/ |
| Rules 33-36 Decisions And Judgments | https://www.gaappeals.gov/rules-33-36/ |
| Rule 37 Reconsideration | https://www.gaappeals.gov/rule-37/ |
| Rule 38 Certiorari | https://www.gaappeals.gov/rule-38/ |
| Rule 39 Remittitur | https://www.gaappeals.gov/rule-39/ |
| Rule 40 Supersedeas and Emergency Motions | https://www.gaappeals.gov/rule-40/ |
| Rule 41 Motions and Responses | https://www.gaappeals.gov/rule-41/ |
| Rule 42 Document Retention | https://www.gaappeals.gov/rule-42/ |
| Rule 43 Parties | https://www.gaappeals.gov/rule-43/ |
| Rule 44 Disqualifications and Recusals | https://www.gaappeals.gov/rule-44/ |
| Rule 45 Expedited Appeals Under The Parental Notification Act | https://www.gaappeals.gov/rule-45/ |
| Rule 46 Electronic Filing Of Documents | https://www.gaappeals.gov/rule-46/ |

## Complete rulebook PDF named elsewhere (not downloaded)

Search results named https://www.gaappeals.gov/wp-content/uploads/2026/03/COA-Rules-Complete-Eff-26-March-26.pdf (and a Spanish companion). It was not fetched. Individual rule pages state the rules are effective March 26, 2026; that date is an index/page label, not independently verified current-law status.

Gap notes: index inventory only. Companion to the 2026-10-13 Supreme Court / Uniform rules index checkpoint. No corpus rows written. Missing DATABASE_URL means no authority rows can be written. Raw byte hashes deferred until a non-captcha fetch is available.
