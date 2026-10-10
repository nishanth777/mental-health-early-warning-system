from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import assessment_bp
from .services import (
    predict_depression,
    get_risk_level,
    generate_recommendations,
)
from .nlp_service import predict_nlp_risk
from .facial_service import predict_facial_emotion

from app.extensions import db
from app.models.assessment import Assessment


@assessment_bp.route("/", methods=["POST"])
@jwt_required()
def submit_assessment():

    identity = get_jwt_identity()

    # --------------------------------------------------------
    # Read assessment data
    # --------------------------------------------------------

    if request.content_type and request.content_type.startswith(
        "multipart/form-data"
    ):
        data = request.form.to_dict()
    else:
        data = request.get_json(silent=True) or {}

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

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
        "journal_text",
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
    # Convert numerical form values
    # --------------------------------------------------------

    try:

        data["sleep_hours"] = float(
            data["sleep_hours"]
        )

        data["sleep_quality"] = int(
            data["sleep_quality"]
        )

        data["stress_level"] = int(
            data["stress_level"]
        )

        data["academic_pressure"] = int(
            data["academic_pressure"]
        )

        data["mood"] = int(
            data["mood"]
        )

        data["energy_level"] = int(
            data["energy_level"]
        )

        data["social_interaction"] = int(
            data["social_interaction"]
        )

        data["exercise_minutes"] = float(
            data["exercise_minutes"]
        )

        data["screen_time"] = float(
            data["screen_time"]
        )

        data["study_hours"] = float(
            data["study_hours"]
        )

    except (TypeError, ValueError):

        return jsonify({
            "error": "Invalid assessment values."
        }), 400

    # --------------------------------------------------------
    # Facial emotion processing
    # --------------------------------------------------------

    facial_emotion = None
    facial_confidence = None
    facial_used = False

    facial_file = request.files.get(
        "facial_image"
    )

    if facial_file and facial_file.filename:

        try:

            facial_result = (
                predict_facial_emotion(
                    facial_file
                )
            )

            facial_emotion = (
                facial_result["emotion"]
            )

            facial_confidence = (
                facial_result["confidence"]
            )

            facial_used = True

            print(
                "📷 Facial emotion detected:",
                facial_emotion
            )

            print(
                "📷 Facial confidence:",
                facial_confidence
            )

        except Exception as exc:

            print(
                "📷 Facial processing error:",
                exc
            )

            facial_emotion = None
            facial_confidence = None
            facial_used = False

    # --------------------------------------------------------
    # Structured ML prediction
    # --------------------------------------------------------

    structured_prediction, structured_risk_score = (
        predict_depression(data)
    )

    # --------------------------------------------------------
    # NLP prediction
    # --------------------------------------------------------

    journal_text = data.get(
        "journal_text",
        ""
    )

    nlp_result = predict_nlp_risk(
        journal_text
    )

    # --------------------------------------------------------
    # Risk fusion
    #
    # Structured model = primary signal
    # NLP = supporting signal
    # Facial emotion = auxiliary affective signal
    #
    # IMPORTANT:
    # Facial emotion is NOT converted into a
    # depression/stress probability.
    # --------------------------------------------------------

    if nlp_result["valid"]:

        nlp_risk_score = (
            nlp_result["risk_score"]
        )

        final_risk_score = (
            (0.70 * structured_risk_score)
            + (0.30 * nlp_risk_score)
        )

        nlp_used = True

    else:

        nlp_risk_score = None

        final_risk_score = (
            structured_risk_score
        )

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

    recommendations = (
        generate_recommendations(
            data,
            final_risk_score
        )
    )

    # --------------------------------------------------------
    # Save assessment
    # --------------------------------------------------------

    assessment = Assessment(

        user_id=identity,

        sleep_hours=data.get(
            "sleep_hours"
        ),

        sleep_quality=data.get(
            "sleep_quality"
        ),

        stress_level=data.get(
            "stress_level"
        ),

        academic_pressure=data.get(
            "academic_pressure"
        ),

        mood=data.get(
            "mood"
        ),

        energy_level=data.get(
            "energy_level"
        ),

        social_interaction=data.get(
            "social_interaction"
        ),

        exercise_minutes=data.get(
            "exercise_minutes"
        ),

        screen_time=data.get(
            "screen_time"
        ),

        study_hours=data.get(
            "study_hours"
        ),

        journal_text=journal_text,

        prediction_score=final_risk_score,

        facial_emotion=facial_emotion,

        facial_confidence=facial_confidence,

        facial_used=facial_used,
    )

    db.session.add(
        assessment
    )

    db.session.commit()

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return jsonify({

        "message":
            "Assessment submitted successfully",

        # Final risk result
        "prediction":
            structured_prediction,

        "risk_score":
            round(
                final_risk_score * 100,
                2
            ),

        "risk_level":
            risk_level,

        # Structured signal
        "structured_risk_score":
            round(
                structured_risk_score * 100,
                2
            ),

        # NLP signal
        "nlp_risk_score":
            (
                round(
                    nlp_risk_score * 100,
                    2
                )
                if nlp_risk_score is not None
                else None
            ),

        "nlp_used":
            nlp_used,

        # Facial signal
        "facial_used":
            facial_used,

        "facial_emotion":
            facial_emotion,

        "facial_confidence":
            (
                round(
                    facial_confidence,
                    4
                )
                if facial_confidence is not None
                else None
            ),

        # NLP validation
        "nlp_validation":
            nlp_result.get(
                "validation"
            ),

        # Recommendations
        "recommendations":
            recommendations

    }), 201


@assessment_bp.route(
    "/history",
    methods=["GET"]
)
@jwt_required()
def assessment_history():

    identity = get_jwt_identity()

    assessments = (
        Assessment.query
        .filter_by(
            user_id=identity
        )
        .order_by(
            Assessment.created_at.desc()
        )
        .all()
    )

    result = []

    for assessment in assessments:

        result.append({

            "id":
                assessment.id,

            "prediction_score":
                round(
                    assessment.prediction_score * 100,
                    2
                ),

            "sleep_hours":
                assessment.sleep_hours,

            "sleep_quality":
                assessment.sleep_quality,

            "stress_level":
                assessment.stress_level,

            "academic_pressure":
                assessment.academic_pressure,

            "mood":
                assessment.mood,

            "energy_level":
                assessment.energy_level,

            "social_interaction":
                assessment.social_interaction,

            "exercise_minutes":
                assessment.exercise_minutes,

            "screen_time":
                assessment.screen_time,

            "study_hours":
                assessment.study_hours,

            "journal_text":
                assessment.journal_text,

            # Facial information
            "facial_emotion":
                assessment.facial_emotion,

            "facial_confidence":
                assessment.facial_confidence,

            "facial_used":
                assessment.facial_used,

            "created_at":
                assessment.created_at.isoformat()
        })

    return jsonify({

        "count":
            len(result),

        "assessments":
            result

    }), 200