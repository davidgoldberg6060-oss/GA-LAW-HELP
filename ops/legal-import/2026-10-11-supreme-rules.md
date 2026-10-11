# Supreme Court of Georgia Rules — discover-only checkpoint

Fetch date: 2026-10-11 (UTC). DATABASE_URL was unset, so no rule PDFs were downloaded and no corpus rows were written.

Source: https://www.gasupreme.us/rules/

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `dee8e118e073ba739bbbc054b79bb4c26f76408e42150b0314249d00daa80efc` | HTML index only |
| amendments page | https://www.gasupreme.us/rules/amendments-to-rules/ | 200 | 1,709,486 | `0704c3f60af6da35638426e6d71cdec89f1ef5a441619030dab18354810f5824` | HTML list of orders |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

Named current-rules link (not downloaded):
- Rules of the Supreme Court (Effective July 2, 2026): https://www.gasupreme.us/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf
- Rule Changes & Amendment History (Chart – 2026 Updates): https://www.gasupreme.us/wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf
- Quick Reference: https://www.gasupreme.us/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf
- Archived Rules (Former Versions): https://www.gasupreme.us/rules/former-rules

Amendments page names recent Uniform Superior Court Rules orders (e.g. October 5, 2026 order amending Rules 4.3, 10.2, and 21, effective November 5, 2026) and other 2026 amendments. Those PDFs were not fetched because robots.txt disallows /wp-content/uploads/.

These are page and link-label checkpoints only, not stored court-rule text, not proof of current law, and not coverage. Lexis was not opened. A missing DATABASE_URL means no authority rows can be written.

Gap notes: index pages only. Full rule text lives in the disallowed uploads PDFs. Currency of the named effective date (July 2, 2026) was not independently verified against a later order. No corpus rows written.
