# GALAWHELP Supabase deployment

The canonical v1.3 migration chain is the ordered set in `supabase/migrations/`,
beginning with `20260920040302_preserve_legacy_prototype_schema.sql` and ending
with `20260920040313_v13_email_verification_security.sql`.
It creates the application schema, indexes, constraints, private Storage bucket,
enables RLS, and removes direct `anon`/`authenticated` access. The FastAPI service
remains the only data-access boundary so owner checks and audit logging cannot be
bypassed from the Android client.

Required production secrets:

- `DATABASE_URL`: Supabase Postgres connection string with `sslmode=require`
- `JWT_SECRET`: independent random value of at least 32 characters
- `ADMIN_EMAILS`: comma-separated application administrators
- `REQUIRE_VERIFIED_EMAIL=true`
- `PUBLIC_APP_URL`: verified HTTPS application origin used in account emails
- SMTP settings from `.env.example` for verification and recovery delivery
- `STORAGE_BACKEND=s3`
- `S3_BUCKET=ga-law-help-evidence`
- `S3_ENDPOINT_URL`: the project's Supabase S3 endpoint
- `AWS_REGION`: the exact project region shown in Supabase Storage S3 settings
- Supabase S3 access key and secret in `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`

Use the direct Storage hostname (`https://<project-ref>.storage.supabase.co/storage/v1/s3`)
and path-style addressing for large-file performance and signature compatibility.
Do not send `x-amz-server-side-encryption`; Supabase's S3 compatibility layer does
not implement that header, while the managed storage service handles encryption at rest.

Never place the database password, service-role key, S3 secret, or JWT secret in
the Android project, Git history, screenshots, or support messages.

Apply every migration in order, including the v1.3 email-verification-token
migration. Its table has RLS enabled and no `anon` or `authenticated` access;
only the protected FastAPI database connection may use it.

Production startup never creates or alters tables. It verifies database
connectivity and requires all 16 migrated application tables before accepting
traffic.

For a persistent container backend, use the direct connection when IPv6 is
available or the shared **session** pooler on IPv4. For serverless deployment,
use the transaction pooler and set `DATABASE_POOL_MODE=transaction`; the backend
then disables Psycopg prepared statements, which transaction mode does not support.
