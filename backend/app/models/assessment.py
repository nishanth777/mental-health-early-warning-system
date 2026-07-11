from datetime import datetime

from app.extensions import db


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="assessments"
    )

    prediction_score = db.Column(db.Float, nullable=False)

    sleep_hours = db.Column(db.Float, nullable=False)
    sleep_quality = db.Column(db.Integer, nullable=False)

    stress_level = db.Column(db.Integer, nullable=False)
    academic_pressure = db.Column(db.Integer, nullable=False)

    mood = db.Column(db.Integer, nullable=False)
    energy_level = db.Column(db.Integer, nullable=False)
    social_interaction = db.Column(db.Integer, nullable=False)

    exercise_minutes = db.Column(db.Integer, nullable=False)

    screen_time = db.Column(db.Float, nullable=False)
    study_hours = db.Column(db.Float, nullable=False)

    journal_text = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )