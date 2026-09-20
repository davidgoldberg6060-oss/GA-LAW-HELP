import os
import smtplib
import ssl
import logging
from email.message import EmailMessage
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


def _public_link(path: str, token: str) -> str:
    base = os.getenv("PUBLIC_APP_URL", "").rstrip("/")
    if not base:
        raise RuntimeError("PUBLIC_APP_URL is required for email delivery")
    return f"{base}{path}?{urlencode({'token': token})}"


def _send(to_email: str, subject: str, text: str) -> bool:
    if os.getenv("MAIL_DELIVERY_MODE", "disabled").lower() != "smtp":
        return False
    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT", "587"))
    sender = os.environ["SMTP_FROM"]
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    message = EmailMessage()
    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text)
    try:
        if os.getenv("SMTP_SSL", "false").lower() == "true":
            with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=15) as client:
                if username: client.login(username, password or "")
                client.send_message(message)
            return True
        with smtplib.SMTP(host, port, timeout=15) as client:
            if os.getenv("SMTP_STARTTLS", "true").lower() == "true":
                client.starttls(context=ssl.create_default_context())
            if username: client.login(username, password or "")
            client.send_message(message)
        return True
    except (OSError, smtplib.SMTPException):
        logger.exception("Account email delivery failed")
        return False


def deliver_verification(to_email: str, token: str) -> bool:
    if os.getenv("MAIL_DELIVERY_MODE", "disabled").lower() != "smtp": return False
    link = _public_link("/verify-email", token)
    return _send(to_email, "Verify your GA.LAW.HELP email", f"Verify your email:\n\n{link}\n\nIf you did not create this account, ignore this message.")


def deliver_password_reset(to_email: str, token: str) -> bool:
    if os.getenv("MAIL_DELIVERY_MODE", "disabled").lower() != "smtp": return False
    link = _public_link("/reset-password", token)
    return _send(to_email, "Reset your GA.LAW.HELP password", f"Reset your password:\n\n{link}\n\nIf you did not request this, ignore this message.")
