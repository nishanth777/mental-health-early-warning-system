from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import assessment_bp
from .services import (
    predict_depression,
    get_risk_level,
    generate_recommendations,
)
from app.extensions import db
from app.models.assessment import Assessment


@assessment_bp.route("/", methods=["POST"])
@jwt_required()
def submit_assessment():

    data = request.get_json()

    identity = get_jwt_identity()

    required_fields = [
        "sleep_hours",
        "sleep_quality",
        "stress_level",
        "academic_pressure",
        "mood",
        "energy_level",
        "social_interaction",
        "exercise_minutes",
        "screen_time",
        "study_hours",
        "journal_text"
    ]

    # Validate required fields
    for field in required_fields:
        if data.get(field) is None:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    # Generate AI prediction
    prediction, risk_score = predict_depression(data)
    risk_level = get_risk_level(risk_score)

    recommendations = generate_recommendations(
    data,
    risk_score
)

    # Save assessment
    assessment = Assessment(
        user_id=identity,
        sleep_hours=data.get("sleep_hours"),
        sleep_quality=data.get("sleep_quality"),
        stress_level=data.get("stress_level"),
        academic_pressure=data.get("academic_pressure"),
        mood=data.get("mood"),
        energy_level=data.get("energy_level"),
        social_interaction=data.get("social_interaction"),
        exercise_minutes=data.get("exercise_minutes"),
        screen_time=data.get("screen_time"),
        study_hours=data.get("study_hours"),
        journal_text=data.get("journal_text"),
        prediction_score=risk_score
    )

    db.session.add(assessment)
    db.session.commit()

    return jsonify({
    "message": "Assessment submitted successfully",
    "prediction": prediction,
    "risk_score": round(risk_score * 100, 2),
    "risk_level": risk_level,
    "recommendations": recommendations
}), 201


@assessment_bp.route("/history", methods=["GET"])
@jwt_required()
def assessment_history():

    identity = get_jwt_identity()

    assessments = (
        Assessment.query.filter_by(user_id=identity)
        .order_by(Assessment.created_at.desc())
        .all()
    )

    result = []

    for assessment in assessments:
        result.append({
            "id": assessment.id,
            "prediction_score": round(assessment.prediction_score * 100, 2),
            "sleep_hours": assessment.sleep_hours,
            "sleep_quality": assessment.sleep_quality,
            "stress_level": assessment.stress_level,
            "academic_pressure": assessment.academic_pressure,
            "mood": assessment.mood,
            "energy_level": assessment.energy_level,
            "social_interaction": assessment.social_interaction,
            "exercise_minutes": assessment.exercise_minutes,
            "screen_time": assessment.screen_time,
            "study_hours": assessment.study_hours,
            "journal_text": assessment.journal_text,
            "created_at": assessment.created_at.isoformat()
        })

    return jsonify({
        "count": len(result),
        "assessments": result
    }), 200