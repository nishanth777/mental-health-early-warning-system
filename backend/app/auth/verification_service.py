import hashlib
import html
import os
import secrets
from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.extensions import db
from app.auth.email_service import send_email


TOKEN_EXPIRY_MINUTES = 30


def create_verification_token(user):
    """Generate a secure token and store only its SHA-256 hash."""
    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    user.email_verification_token_hash = token_hash

    user.email_verification_expires_at = (
        datetime.now(timezone.utc).replace(tzinfo=None)
        + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    )

    db.session.commit()

    return token


def send_verification_email(user):
    """Send an email containing the verification link."""
    token = create_verification_token(user)

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    ).rstrip("/")

    verification_link = (
        f"{frontend_url}/verify-email?token={token}"
    )

    # Escape user-provided text before inserting it into HTML.
    safe_name = html.escape(user.full_name or "Student")

    html_content = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 600px;
        margin: auto;
        padding: 30px;
        color: #333;
        line-height: 1.6;
    ">
        <h2>Verify your email address</h2>

        <p>Hello {safe_name},</p>

        <p>
            Thank you for registering.
            Please verify your email address to activate
            your account.
        </p>

        <p style="margin: 30px 0;">
            <a
                href="{verification_link}"
                style="
                    background: #8b5cf6;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 8px;
                    display: inline-block;
                "
            >
                Verify Email
            </a>
        </p>

        <p>
            This link expires in
            {TOKEN_EXPIRY_MINUTES} minutes.
        </p>

        <p>
            If you did not create this account,
            you can safely ignore this email.
        </p>
    </div>
    """

    return send_email(
        to_email=user.email,
        subject="Verify your email address",
        html_content=html_content
    )


def verify_token(token):
    """Validate a token and mark the associated account verified."""
    if not token or not isinstance(token, str):
        return False

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    user = User.query.filter_by(
        email_verification_token_hash=token_hash
    ).first()

    if not user:
        return False

    expires_at = user.email_verification_expires_at

    # Reject missing or expired tokens.
    if not expires_at or datetime.utcnow() >= expires_at:
        user.email_verification_token_hash = None
        user.email_verification_expires_at = None
        db.session.commit()
        return False

    user.email_verified = True
    user.email_verified_at = datetime.utcnow()

    # Make the token single-use.
    user.email_verification_token_hash = None
    user.email_verification_expires_at = None

    db.session.commit()

    return True