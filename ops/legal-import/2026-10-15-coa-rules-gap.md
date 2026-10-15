# Court of Appeals rules and opinion search — discover-only gap checkpoint (2026-10-15)

DATABASE_URL was unset. No rule PDFs, opinion PDFs, or other authority files were downloaded. No corpus rows were written. This is not stored rule or opinion text and not current-law verification.

Direct HTTP fetch of https://www.gaappeals.gov/rules/ and https://www.gaappeals.gov/opinion-search/ returned HTTP 405 with AWS WAF captcha challenge (CloudFront). robots.txt allows most paths (disallows only /wp-admin/) but the WAF still blocks automated access. A prior browser-style fetch of the rules landing page observed Rules 1-8 General content stating the rules are effective March 26, 2026, plus a Spanish complete-rulebook PDF link. Opinion search is an interactive docket-by-date form that points to a separate Docket/Case Inquiry System. Neither page was fully captured as stable bytes in this pass; no SHA-256 of the live HTML is recorded because of the WAF block.

Prior 2026-10-08 checkpoint noted HTTP 405 on the same opinion-search and rules indexes. Companion Supreme Court other-court-rules index (2026-10-13) already lists Uniform rules and points to www.gaappeals.gov for Court of Appeals rules.

Gap notes: Court of Appeals rulebook and opinion indexes remain uningested. No Lexis annotations were opened. Missing DATABASE_URL means no authority rows can be written even if files were obtained. These counts are not persisted coverage.
