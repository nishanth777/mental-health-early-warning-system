from datetime import datetime

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    provider = db.Column(db.String(50), nullable=False, default="email")
    role = db.Column(db.String(50), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Email verification
    email_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false()
    )
    email_verified_at = db.Column(db.DateTime, nullable=True)

    # Secure verification token storage
    email_verification_token_hash = db.Column(
        db.String(64),
        nullable=True
    )
    email_verification_expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    assessments = db.relationship(
        "Assessment",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan"
    )