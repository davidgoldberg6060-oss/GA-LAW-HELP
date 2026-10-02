# Guest public rights flow

Free research and encounter help must not require an account.

- Web landing `Free research` calls `runResearch`, which uses `guestRightsAndEncounter` in `src/guestPublic.ts`. That helper calls `POST /public/rights-assistant` and `GET /public/encounter` and does not send an Authorization header.
- `vite.config.ts` still rewrites any leftover login gate at compile time. Source no longer opens the account dialog for Free research.
- Android home opens without a session. Talk to Me and Know My Rights call GuestPublicApi. Private cases, documents, recordings, and motion screening still call requirePaid.
- Android `GuestPublicApi` and `GroundedLegalMode` use the same public paths for rights and talk-to-me. Know your rights does not require sign-in.
- If the corpus database query fails, `POST /public/rights-assistant` returns the encounter pack with an explicit coverage notice and no invented citation. It does not open a login gate.
- Private cases, evidence, and `/cases/{id}/motion-screen` stay on the authenticated client.
- This is general legal information. It is not a substitute for a licensed Georgia attorney. Do not resist, lie, or destroy evidence.
- Issue 88 corpus coverage is separate: an empty index must surface a coverage notice rather than invented citations. A missing `DATABASE_URL` is not recorded as ingested coverage.
- Regression: `tests/test_guest_free_research_browser_path.py`.
