# GA.LAW.HELP Owner Access

GA.LAW.HELP uses server-side roles for owner access. There is no universal master password embedded in the Android application.

## Access model

- `admin`: Owner/administrator account. Full paid-feature access without a Stripe subscription.
- `paid`: Customer with an active membership. Full paid-feature access.
- `user`: Standard account. Paid features remain locked until membership is active.

The backend `/billing/status` endpoint is the source of truth for paid access. It treats both `paid` and `admin` roles as paid access. The Android client must continue to rely on this server response rather than an email address, hard-coded password, or client-side owner flag.

## Owner sign-in

The owner signs in through the normal GA.LAW.HELP login screen using the credentials for the account that has the `admin` role. After authentication, billing status reports paid access and the app unlocks paid features without checkout.

## Security requirement

Never add a master password, owner password, Stripe bypass token, or privileged email address to the APK/source as an access-control mechanism. Owner privileges must be assigned and enforced server-side.

## UI requirement

When the authenticated profile role is `admin`, the UI may label the account `Owner / Admin` and `Full access — no subscription required`. This label is informational only; authorization must remain server-side.
