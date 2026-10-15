# Court of Appeals rules index — discover-only checkpoint

Fetch date: 2026-10-15 06:01 UTC. DATABASE_URL was unset, so no rule pages were downloaded and no corpus rows were written.

Direct fetch of https://www.gaappeals.gov/court-rules/ and https://www.gaappeals.gov/robots.txt with the corpus user agent returned AWS WAF captcha (HTTP 405, header x-amzn-waf-action: captcha, Content-Length 2511).

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| court-rules index (captcha) | https://www.gaappeals.gov/court-rules/ | 405 | 2,511 | `bfd81c15e1401e9cfabe9502546bcb412e3aa622e47403eb62f054cd4528749a` | WAF captcha body, not official index |
| robots.txt (captcha) | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `5e29cde93589d42721d4ea83f0ed9dfcdbbc368e351a71ac5155b80355237ae3` | WAF captcha body, not official robots |

A secondary retrieval of the index URL listed these rule-page links (labels only; official page bytes not hashed; pages not downloaded; not stored rule text):

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

Sample pages state the rules are effective on March 26, 2026. Lexis was not opened. These counts are not persisted coverage. Gap: WAF blocks automated fetch of the official index and rule pages; no rule text stored. Missing DATABASE_URL means no authority rows can be written.
