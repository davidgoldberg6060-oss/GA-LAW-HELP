from app.billing import checkout_configured, checkout_options


def configure_common(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_example")
    monkeypatch.setenv("PUBLIC_APP_URL", "https://example.com")


def test_monthly_plan_uses_legacy_price_fallback(monkeypatch):
    configure_common(monkeypatch)
    monkeypatch.delenv("STRIPE_MONTHLY_PRICE_ID", raising=False)
    monkeypatch.setenv("STRIPE_PRICE_ID", "price_monthly")
    assert checkout_configured("monthly") is True
    assert checkout_configured("annual") is False
    options = checkout_options()
    assert options["checkout_configured"] is True
    assert options["monthly_available"] is True
    assert options["annual_available"] is False


def test_monthly_label(monkeypatch):
    configure_common(monkeypatch)
    monkeypatch.setenv("STRIPE_MONTHLY_PRICE_ID", "price_monthly")
    monkeypatch.setenv("MEMBERSHIP_MONTHLY_LABEL", "$14.99 / month")
    options = checkout_options()
    assert options["monthly_available"] is True
    assert options["annual_available"] is False
    assert options["monthly_label"] == "$14.99 / month"


def test_annual_price_env_does_not_enable_annual_plan(monkeypatch):
    configure_common(monkeypatch)
    monkeypatch.setenv("STRIPE_MONTHLY_PRICE_ID", "price_monthly")
    monkeypatch.setenv("STRIPE_ANNUAL_PRICE_ID", "price_annual")
    assert checkout_configured("annual") is False
    assert checkout_options()["annual_available"] is False


def test_checkout_disabled_without_common_stripe_config(monkeypatch):
    for name in ("STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "PUBLIC_APP_URL", "STRIPE_PRICE_ID", "STRIPE_MONTHLY_PRICE_ID", "STRIPE_ANNUAL_PRICE_ID"):
        monkeypatch.delenv(name, raising=False)
    assert checkout_configured() is False
