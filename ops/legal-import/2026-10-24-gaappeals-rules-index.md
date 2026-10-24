# Court of Appeals rules index inventory — 2026-10-24

DATABASE_URL was unset, so no corpus rows were written. Discover-only. No rule text was stored.

## Source

- New domain: https://www.gaappeals.gov/ (transitioned from gaappeals.us)
- Rules pages: https://www.gaappeals.gov/rules-1-8/ (and sibling section pages)
- Rules effective March 26, 2026 (per rendered content from prior browser fetch)
- robots.txt: https://www.gaappeals.gov/robots.txt

## Raw fetch (2026-10-24 ~12:01 UTC)

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules page (raw) | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `376ac71b06f16c50fc095522048fe45441fa033b37849e582074de2af2314007` | AWS WAF captcha (Human Verification); x-amzn-waf-action: captcha |
| robots.txt (raw) | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `b353987e97eb3949a643473365254c95caf52a23ba938adcaf3be3e71674feaa` | Same AWS WAF captcha |

## Notes

- Raw unauthenticated fetch from this environment received the AWS WAF captcha challenge. No rule HTML or PDFs were retrieved.
- Prior browser-mediated access (not recorded as raw bytes) showed HTML rules pages effective March 26, 2026, with Spanish PDF link under /wp-content/uploads/.
- robots.txt (when reachable) disallows only /wp-admin/; however, raw access is currently captcha-blocked.
- Lexis was not opened. No annotations scraped.
- Gap: rules text is not yet checkpointed as raw source bytes; future importer must handle WAF or use an authorized path. Currency must be verified against the official site.
- This is an inventory of the official rules access point only; no rule text stored, no coverage claimed.

Not stored rule text and not current-law verification.
