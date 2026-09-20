# v1.3 account-security increment

This increment completes the application-side foundation for email verification
and password recovery. Tokens are random, stored only as SHA-256 hashes, expire,
and are single-use. Issuing a replacement invalidates older unused tokens.

Production can require verified email with `REQUIRE_VERIFIED_EMAIL=true`. The
SMTP adapter sends links rooted at `PUBLIC_APP_URL`; secrets stay in environment
variables and must never enter Android resources or Git history.

Refresh-token rotation now treats reuse of an already-rotated token as a
possible theft signal and revokes the user's remaining sessions. Password reset
also revokes every active refresh token.

The Android client exposes verification, resend, forgot-password, and reset
screens. Production still needs a verified HTTPS domain, real SMTP credentials,
deep-link polish, MFA, rate limiting at the gateway, delivery monitoring, and an
independent security review.
