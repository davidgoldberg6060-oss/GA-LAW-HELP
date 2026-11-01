from app import email_delivery


def test_send_skips_when_smtp_host_missing(monkeypatch):
    monkeypatch.setenv("MAIL_DELIVERY_MODE", "smtp")
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)
    monkeypatch.setenv("PUBLIC_APP_URL", "https://example.com")
    assert email_delivery.deliver_verification("a@example.com", "tok") is False
    assert email_delivery.deliver_password_reset("a@example.com", "tok") is False
