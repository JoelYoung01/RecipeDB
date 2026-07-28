"""Transactional email helpers. Falls back to logging when SMTP is unset."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from api.core.config import settings

logger = logging.getLogger(__name__)


def emails_enabled() -> bool:
    return bool(settings.SMTP_HOST and settings.EMAILS_FROM_EMAIL)


def send_email(to: str, subject: str, body: str) -> None:
    """Send an email via SMTP when configured; always log in development."""
    if settings.ENVIRONMENT == "development" or not emails_enabled():
        logger.info(
            "Email to=%s subject=%r body=%r (smtp_enabled=%s)",
            to,
            subject,
            body,
            emails_enabled(),
        )

    if not emails_enabled():
        return

    message = EmailMessage()
    message["From"] = (
        f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        if settings.EMAILS_FROM_NAME
        else settings.EMAILS_FROM_EMAIL
    )
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    if settings.SMTP_SSL:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
            server.send_message(message)
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
            server.send_message(message)


def send_verification_otp_email(to: str, otp: str) -> None:
    subject = f"Your {settings.PROJECT_NAME} verification code"
    body = (
        f"Your verification code is: {otp}\n\n"
        f"This code expires in {settings.EMAIL_OTP_EXPIRE_MINUTES} minutes.\n"
        "If you did not create an account, you can ignore this email.\n"
    )
    send_email(to=to, subject=subject, body=body)
