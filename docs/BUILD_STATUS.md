# Build Status — v1.3.0 production foundation

## Live foundation deployment — 2026-09-20

- GitHub `main` contains the complete v1.3 production foundation.
- GitHub Actions backend CI passes.
- The `GALAWHELP` Supabase project contains all 16 v1.3 public application tables.
- Every public application table has RLS enabled; `anon` and `authenticated` have no direct table grants.
- The earlier empty five-table prototype is preserved in the access-restricted `legacy` schema.
- Repository migration versions match the live Supabase migration history.

Implemented and verified in this increment:
- Native Android registration and login against the FastAPI backend
- Android Keystore-backed encrypted access/refresh token storage and refresh rotation
- Authenticated case listing and case creation
- Case workspace with timeline/evidence retrieval
- Android system document picker for photos, PDFs, audio, screen recordings and video
- Multipart and resumable/chunked evidence upload to the authenticated case API
- Backend SHA-256 integrity hashing and original-file preservation already wired into the upload path
- Server-side refresh-token revocation on logout
- Owner-isolation and end-to-end API tests
- Evidence byte limits, SHA-256 re-verification endpoint, and queued analysis jobs
- Admin-only legal-authority ingestion
- Supabase/PostgreSQL migration with RLS locked against direct mobile access
- Supabase CLI 2.117-compatible PostgreSQL 17 configuration and S3 protocol configuration
- Supabase S3 path-style signing without unsupported server-side-encryption headers
- Complete foreign-key indexing and locked-down current/future Data API sequence grants
- Direct/session/transaction connection-mode handling with prepared statements disabled for transaction pooling
- CI workflow and Gradle wrapper
- Eight passing backend and configuration tests
- API base URL supplied as Android BuildConfig for deployment
- Email verification token lifecycle and enumeration-safe resend endpoint
- SMTP delivery adapter for verification and password-recovery links
- Android verification and password-reset screens
- Refresh-token reuse detection with account-wide session revocation
- Idempotency guards for completed resumable uploads

Still required before production release:
- Production HTTPS domain/backend configuration and live connectivity verification
- S3-compatible encrypted object storage instead of local server disk
- production SMTP/domain configuration and MFA
- background/resumable uploads for very large video
- worker queue and media-analysis pipeline
- Georgia official-source ingestion/versioning and legal citation retrieval
- AI research, Why? citations, Second-Look, Red-Team and contradiction engine
- automated tests, security review, privacy policy/terms, Play Store signing/listing and production review
