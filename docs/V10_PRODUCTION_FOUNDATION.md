# v1.0 Production Foundation

Added a storage abstraction for private S3-compatible evidence storage with server-side encryption, rotating refresh tokens, enumeration-safe password-reset endpoints, session revocation after password reset, a separate background-worker service, PostgreSQL health checks, and production-oriented environment configuration.

## Still requires external configuration before production
- Private cloud bucket and credentials/KMS policy
- Transactional email/SMS provider for reset-token delivery
- TLS/domain/reverse proxy
- Secrets manager (do not deploy `.env` secrets in source control)
- Real media/AI analysis providers wired into `worker.py`
- MFA enrollment/challenge implementation
- Database migrations and backup/restore drills
- Security review/penetration testing and Play Store privacy/data-safety materials

No code in this version claims those external services are already connected.
