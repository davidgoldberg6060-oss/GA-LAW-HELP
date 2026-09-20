# v1.1 security and Supabase increment

This increment closes the API startup failure and adds a deployable Supabase
contract. It also adds Argon2id password hashes with legacy bcrypt verification,
JWT issuer/audience/JTI validation, refresh-token rotation/revocation, admin-only
authority ingestion, owner-scoped integration tests, request/security headers,
evidence byte limits and integrity re-verification.

The Android client now keeps both tokens in Android Keystore-backed encrypted
preferences, retries ordinary API calls after token rotation, uses HTTPS outside
debug builds, and uploads large evidence through the chunked API.

Not represented as complete: live migration application, mail/SMS recovery
delivery, MFA, malware scanning, model/media providers, exhaustive Georgia legal
source ingestion, production deployment, or an independent security/legal-data review.
