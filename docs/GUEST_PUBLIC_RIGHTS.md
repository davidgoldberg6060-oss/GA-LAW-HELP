# Guest public rights flow

Free research and encounter help must not require an account.

- Web compile-time rewrite: `vite.config.ts` points the landing `Free research` button and encounter helper at `guestPublic.ts`, which calls `POST /public/rights-assistant` and `GET /public/encounter`.
- Android already uses `GuestPublicApi` for the same paths.
- Private cases, evidence, and `/cases/{id}/motion-screen` stay on the authenticated client.
- This is general legal information. It is not a substitute for a licensed Georgia attorney. Do not resist, lie, or destroy evidence.
- Issue 88 corpus coverage is separate: an empty index must surface a coverage notice rather than invented citations.
