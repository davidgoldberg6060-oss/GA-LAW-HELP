# Court of Appeals of Georgia access inventory — 2026-10-25

DATABASE_URL was unset, so no corpus rows were written. Discover-only. No opinion PDFs, no rule text, and no docket records were downloaded.

## Source

- Homepage / docket-search shell: https://gaappeals.us/
- Opinion search (linked): https://www.gaappeals.gov/opinion-search/
- Rules (linked): https://www.gaappeals.gov/rules-1-8/
- Docket search (linked): https://www.gaappeals.gov/docket-search/

## Raw fetch of homepage (2026-10-25 ~02:01 UTC)

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage (raw, TLS verify bypassed) | https://gaappeals.us/ | 200 | 39,314 | `4c92b0d07ca7b0a76fd30ecdb37fbdfebaa77cb8e4a05685b4768b7f710d3d15` | Serves docket-search page shell; title "Docket Search – Court of Appeals of the State of Georgia"; links to .gov opinion-search, rules, and docket-search. Cert chain verification failed (self-signed in chain); fetch continued. |

## Notes

- https://www.gaappeals.gov/opinion-search/ and /rules-1-8/ returned AWS WAF Human Verification captcha (2,511 bytes); no content retrieved, no PDFs counted.
- The .us site is the public access point that surfaces the official .gov search and rules links.
- Per project policy, no private docket data and no non-public records are fetched.
- Gap: opinion text and current rules remain behind WAF / login-gated or PDF-only paths; bulk public opinion index not yet confirmed accessible without interaction. Preferred public sources for opinions remain CourtListener / official published indexes once accessible without captcha.
- No corpus coverage claimed. Not stored opinion or rule text and not current-law verification.
