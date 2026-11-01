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
    host = os.getenv("SMTP_HOST", "").strip()
    sender = os.getenv("SMTP_FROM", "").strip()
    if not host or not sender:
        logger.warning("MAIL_DELIVERY_MODE=smtp but SMTP_HOST/SMTP_FROM is not set; skipping email delivery")
        return False
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError:
        logger.warning("Invalid SMTP_PORT; skipping email delivery")
        return False
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



def deliver_encounter_notice(to_email: str, filename: str, sha256: str, size_bytes: int) -> bool:
    """Notify the account owner that an encounter recording was preserved.

    Large evidence files should remain in protected evidence storage rather than
    being attached to email. A separate authenticated download route can be
    linked here once that route is available.
    """
    subject = "GA.LAW.HELP encounter recording preserved"
    text = (
        "Your encounter recording was preserved by GA.LAW.HELP.\n\n"
        f"File: {filename}\n"
        f"Size: {size_bytes} bytes\n"
        f"SHA-256: {sha256}\n\n"
        "The protected app copy remains preserved. Do not forward sensitive "
        "evidence unless you intend to share it."
    )
    return _send(to_email, subject, text)

def deliver_verification(to_email: str, token: str) -> bool:
    if os.getenv("MAIL_DELIVERY_MODE", "disabled").lower() != "smtp": return False
    link = _public_link("/verify-email", token)
    return _send(to_email, "Verify your GA.LAW.HELP email", f"Verify your email:\n\n{link}\n\nIf you did not create this account, ignore this message.")


def deliver_password_reset(to_email: str, token: str) -> bool:
    if os.getenv("MAIL_DELIVERY_MODE", "disabled").lower() != "smtp": return False
    link = _public_link("/reset-password", token)
    return _send(to_email, "Reset your GA.LAW.HELP password", f"Reset your password:\n\n{link}\n\nIf you did not request this, ignore this message.")
