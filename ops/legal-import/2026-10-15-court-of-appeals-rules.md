# Court of Appeals rules inventory checkpoint (2026-10-15)

Fetch date: 2026-10-15 (UTC). DATABASE_URL is unset. No authority rows were written. No rule text was stored as corpus. This is not current-law verification.

Raw non-browser fetches of gaappeals.gov return HTTP 405 with `x-amzn-waf-action: captcha` (CloudFront). robots.txt allows most paths (disallows only `/wp-admin/`). The complete rules PDF and several HTML section pages are readable through a non-raw fetch that extracts text; source-byte hashes were not obtained because the raw download is blocked by the WAF.

## Complete rules publication

- URL: https://www.gaappeals.gov/wp-content/uploads/2026/03/COA-Rules-Complete-Eff-26-March-26.pdf
- Title: Georgia Court of Appeals Rules, effective March 26, 2026
- Table of contents names rules 1–46 in these divisions: I. General (1–8); II. Attorneys (9–10); III. Dockets and Calendars (11–15); IV. Extension of Time (16); V. Records and Transcripts (17–21); VI. Reserved (22); VII. Briefs (23–27); VIII. Argument (28–29); IX. Interlocutory Applications (30); X. Discretionary Applications (31); XI. Transfer (32); XII. Decisions and Judgments (33–36); XIII. Reconsideration (37); XIV. Certiorari (38); XV. Remittitur (39); XVI. Supersedeas and Emergency Motions (40); XVII. Motions and Responses (41); XVIII. Document Retention (42); XIX. Parties (43); XX. Disqualifications and Recusals (44); XXI. Expedited Appeals under the Parental Notification Act (45); XXII. Electronic Filing (46).
- Related: Spanish complete rules PDF linked from the rules-1-8 page (https://www.gaappeals.gov/wp-content/uploads/2026/03/ES-MX.completerulebook-32126-Final-1.pdf). Not downloaded as bytes. Redline order of 25 February 2026 also exists; not fetched as bytes.

## HTML section pages observed

| Label | URL | Notes |
| --- | --- | --- |
| Rules 1–8: General | https://www.gaappeals.gov/rules-1-8/ | Effective 26 March 2026; text extractable |
| Rules 11–15: Dockets and Calendars | https://www.gaappeals.gov/rules-11-15/ | Effective 26 March 2026; text extractable |
| Rules 23–27: Briefs | https://www.gaappeals.gov/rules-23-27/ | Effective 26 March 2026 |
| Rules 33–36: Decisions and Judgments | https://www.gaappeals.gov/rules-33-36/ | Effective 26 March 2026 |
| Rule 30: Interlocutory Applications | https://www.gaappeals.gov/rule-30/ | Effective 26 March 2026 |
| Rule 37 | https://www.gaappeals.gov/rule-37/ | Named in post-sitemap |
| Rule 40: Supersedeas and Emergency Motions | https://www.gaappeals.gov/rule-40/ | Effective 26 March 2026 |

## Gap notes

- Source-byte SHA-256 and exact byte counts are unavailable for the complete PDF and HTML pages because raw fetch hits the AWS WAF captcha (HTTP 405).
- Full set of HTML section URLs was not exhaustively walked; the complete PDF table of contents is the authoritative inventory of rule numbers.
- No rule text was written to the corpus. Missing DATABASE_URL means no authority rows can be created.
- Lexis was not opened. These labels are not persisted coverage and are not a claim that the rules are current or binding for any particular case.
