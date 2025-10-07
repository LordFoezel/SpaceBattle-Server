from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Response

from app.core.errors import AppHttpStatus
from app.core.openapi import with_errors
from app.core.mailer import send_mail
from app.core.email_templates import render_action_email_html, render_action_email_text
from app.models.auth import EmailRequest
from app.repositories import users as users_repo


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/forgot-password-email",
    status_code=AppHttpStatus.NO_CONTENT,
    response_class=Response,
    responses=with_errors({AppHttpStatus.NO_CONTENT: {"description": "Email sent if user exists"}}),
)
def forgot_password_email(payload: EmailRequest) -> Response:
    """Trigger a password reset email. Returns 204 regardless of existence.

    This avoids leaking whether an email is registered.
    """
    try:
        user = users_repo.get_one({"email": payload.email})
        if user:
            base_url = os.getenv("APP_BASE_URL", os.getenv("FRONTEND_URL", "http://localhost:3000")).rstrip("/")
            reset_link = f"{base_url}/reset-password?email={payload.email}"
            subject = "Passwort zurücksetzen"
            text = (
                "Wir haben eine Anfrage zum zurücksetzen deines Passworts erhalten.\n\n"
                f"Falls du das warst, klicke auf den folgenden Link:\n{reset_link}\n\n"
                "Wenn du diese Anfrage nicht gestellt hast, kannst du diese E-Mail ignorieren."
            )
            # Beautified email using HTML template
            subject = "Passwort zurücksetzen"
            heading = "Passwort zurücksetzen"
            body_lines = [
                "Wir haben eine Anfrage zum Zurücksetzen deines Passworts erhalten.",
                "Wenn du das warst, klicke auf den Button unten.",
                "Wenn du diese Anfrage nicht gestellt hast, ignoriere diese E‑Mail.",
            ]
            footer_lines = [
                "Aus Sicherheitsgründen läuft der Link nach einiger Zeit ab.",
            ]
            text = render_action_email_text(
                heading=heading,
                body_lines=body_lines,
                action_text="Passwort jetzt zurücksetzen",
                action_url=reset_link,
                footer_lines=footer_lines,
            )
            html = render_action_email_html(
                title=subject,
                heading=heading,
                body_lines=body_lines,
                action_text="Passwort jetzt zurücksetzen",
                action_url=reset_link,
                footer_lines=footer_lines,
            )
            send_mail(to=payload.email, subject=subject, text=text, html=html)
    except Exception:
        # Do not leak internal errors; still return 204 to the client
        logging.exception("Failed to send forgot-password email")
    return Response(status_code=AppHttpStatus.NO_CONTENT)


@router.post(
    "/verification-email",
    status_code=AppHttpStatus.NO_CONTENT,
    response_class=Response,
    responses=with_errors({AppHttpStatus.NO_CONTENT: {"description": "Verification email sent if user exists"}}),
)
def send_verification_email(payload: EmailRequest) -> Response:
    """Send a verification email for a user account.

    Always returns 204 to avoid user enumeration.
    """
    try:
        user = users_repo.get_one({"email": payload.email})
        if user and not user.verified:
            base_url = os.getenv("APP_BASE_URL", os.getenv("FRONTEND_URL", "http://localhost:3000")).rstrip("/")
            verify_link = f"{base_url}/verify?email={payload.email}"
            subject = "E-Mail-Adresse bestätigen"
            heading = "E-Mail bestätigen"
            body_lines = [
                "Bitte bestätige deine E-Mail-Adresse, um dein Konto zu aktivieren.",
            ]
            footer_lines = [
                f"Falls du dich nicht registriert hast, ignoriere diese E-Mail.",
            ]
            text = render_action_email_text(
                heading=heading,
                body_lines=body_lines,
                action_text="E-Mail jetzt bestätigen",
                action_url=verify_link,
                footer_lines=footer_lines,
            )
            html = render_action_email_html(
                title=subject,
                heading=heading,
                body_lines=body_lines,
                action_text="E-Mail jetzt bestätigen",
                action_url=verify_link,
                footer_lines=footer_lines,
            )
            send_mail(to=payload.email, subject=subject, text=text, html=html)
    except Exception:
        logging.exception("Failed to send verification email")
    return Response(status_code=AppHttpStatus.NO_CONTENT)
