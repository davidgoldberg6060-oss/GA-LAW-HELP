# v1.2 Supabase compatibility increment

Validated against the 2026-09-19 Supabase changelog, current RLS guidance,
current Postgres connection guidance, current S3 authentication/compatibility
documentation, and Supabase CLI 2.117.0.

Changes:

- PostgreSQL 17 local configuration and S3 protocol enablement.
- S3 Signature V4 with forced path-style addressing.
- Removed `x-amz-server-side-encryption`, which Supabase's S3 compatibility API rejects.
- Added every missing foreign-key index.
- Revoked direct Data API access to current and future public tables and sequences.
- Added safe direct/session/transaction pool handling; transaction mode disables Psycopg prepared statements.
- Added project-scoped Supabase MCP configuration.
- Added storage and database configuration tests.

Verification: eight tests pass and both SQL migration files parse successfully.
Live project application and advisors remain pending until live database actions
are available in the connected session.
