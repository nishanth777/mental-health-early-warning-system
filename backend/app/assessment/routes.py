from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import assessment_bp
from .services import (
    predict_depression,
    get_risk_level,
    generate_recommendations,
)
from .nlp_service import predict_nlp_risk

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

    # --------------------------------------------------------
    # Validate required fields
    # --------------------------------------------------------

    for field in required_fields:
        if data.get(field) is None:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    # --------------------------------------------------------
    # Structured ML prediction
    # --------------------------------------------------------

    structured_prediction, structured_risk_score = (
        predict_depression(data)
    )

    # --------------------------------------------------------
    # NLP prediction
    # --------------------------------------------------------

    journal_text = data.get("journal_text", "")

    nlp_result = predict_nlp_risk(
        journal_text
    )

    # --------------------------------------------------------
    # Risk fusion
    # --------------------------------------------------------
    #
    # Structured model is the primary signal.
    # NLP is used as a supporting signal only when
    # the journal passes validation.
    #

    if nlp_result["valid"]:

        nlp_risk_score = nlp_result["risk_score"]

        final_risk_score = (
            (0.70 * structured_risk_score)
            + (0.30 * nlp_risk_score)
        )

        nlp_used = True

    else:

        nlp_risk_score = None

        # If journal text is invalid/low-information,
        # rely entirely on the structured assessment.
        final_risk_score = structured_risk_score

        nlp_used = False

    # --------------------------------------------------------
    # Final risk level
    # --------------------------------------------------------

    risk_level = get_risk_level(
        final_risk_score
    )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = generate_recommendations(
        data,
        final_risk_score
    )

    # --------------------------------------------------------
    # Save assessment
    # --------------------------------------------------------

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
        journal_text=journal_text,
        prediction_score=final_risk_score
    )

    db.session.add(assessment)
    db.session.commit()

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return jsonify({
        "message": "Assessment submitted successfully",

        # Final multimodal result
        "prediction": structured_prediction,
        "risk_score": round(
            final_risk_score * 100,
            2
        ),
        "risk_level": risk_level,

        # Individual model signals
        "structured_risk_score": round(
            structured_risk_score * 100,
            2
        ),

        "nlp_risk_score": (
            round(nlp_risk_score * 100, 2)
            if nlp_risk_score is not None
            else None
        ),

        "nlp_used": nlp_used,

        # NLP validation information
        "nlp_validation": nlp_result.get(
            "validation"
        ),

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

            "prediction_score": round(
                assessment.prediction_score * 100,
                2
            ),

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