# STANDALONE ASSISTANT GA.LAW.HELP — Control and Recovery Plan

This plan supports the ownership record naming Treyvon Pattillo as the product owner. It does not change the separately documented economic revenue-share arrangement or third-party rights.

## Control rules

1. GitHub, Railway, Supabase, domain, app-store, payment, email, and AI-provider accounts must be owned by Treyvon Pattillo or by a company he owns and formally designates.
2. Each account must use a unique password, phishing-resistant multi-factor authentication where offered, and offline recovery codes stored in two secure locations.
3. No developer, contractor, collaborator, or automated service receives owner credentials. Grant only the minimum named role needed and remove access promptly when work ends.
4. The repository remains private unless Treyvon Pattillo deliberately approves publication. The `main` branch should require passing checks and Code Owner approval; force-pushes and branch deletion should be blocked.
5. Production deployments come only from reviewed commits on the protected branch. Secrets remain in server-side secret stores and never in source code, mobile packages, browser bundles, screenshots, logs, or support messages.
6. Keep independent encrypted backups of source releases, database exports, private-object metadata, ownership documents, signed agreements, store records, and domain/hosting receipts. Test restoration regularly.
7. Preserve Git history and release hashes as a dated chain of development. Tag production releases and keep the matching build artifacts and dependency inventory.
8. Material outside contributions require a signed assignment or license defining ownership before they are merged when exclusive project ownership is intended.

## Recovery inventory

Maintain an offline inventory containing only account names, recovery procedures, billing owner, renewal dates, and emergency contacts. Do not put passwords, private keys, recovery codes, tokens, or secret values in this repository.

At minimum, inventory these control points:

- GitHub repository and organization/account;
- Railway project and workspace;
- Supabase project, database, storage, and backups;
- domain registrar and DNS;
- Google Play / other app-store developer accounts and signing-key custody;
- business email and transactional-email provider;
- payment processor and payout account;
- AI/model provider account;
- copyright, trademark, company, and signed contributor/revenue-share records.

## Incident rule

If ownership or account access is threatened: stop new deployments, rotate affected credentials, revoke unknown sessions and collaborators, preserve audit logs, restore from a known release if necessary, and document the event without exposing private case data.

No technical control can make theft or a legal dispute impossible. These measures reduce that risk and preserve evidence of ownership and chain of control.
