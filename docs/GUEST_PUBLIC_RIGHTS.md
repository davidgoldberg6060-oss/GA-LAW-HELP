# Guest public rights flow

Free research and encounter help must not require an account.

- Web compile-time rewrite: `vite.config.ts` points the landing `Free research` button and encounter helper at `guestPublic.ts`, which calls `POST /public/rights-assistant` and `GET /public/encounter`.
- Android already uses `GuestPublicApi` for the same paths, including Know your rights without signing in.
- If the corpus database query fails, `POST /public/rights-assistant` returns the encounter pack with an explicit coverage notice and no invented citation. It does not open a login gate.
- Private cases, evidence, and `/cases/{id}/motion-screen` stay on the authenticated client.
- This is general legal information. It is not a substitute for a licensed Georgia attorney. Do not resist, lie, or destroy evidence.
- Issue 88 corpus coverage is separate: an empty index must surface a coverage notice rather than invented citations. A missing `DATABASE_URL` is not recorded as ingested coverage.
