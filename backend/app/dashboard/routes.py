from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from . import dashboard_bp
from app.models.assessment import Assessment


@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def dashboard():

    identity = get_jwt_identity()

    # Get all assessments (latest first)
    assessments = (
        Assessment.query.filter_by(user_id=identity)
        .order_by(Assessment.created_at.desc())
        .all()
    )

    if not assessments:
        return jsonify({
            "message": "No assessments found."
        }), 404

    total_assessments = len(assessments)

    latest_assessment = assessments[0]

    previous_assessment = None
    if len(assessments) > 1:
        previous_assessment = assessments[1]

    # Calculate averages
    avg_sleep = (
        Assessment.query.with_entities(
            func.avg(Assessment.sleep_hours)
        )
        .filter_by(user_id=identity)
        .scalar()
    )

    avg_stress = (
        Assessment.query.with_entities(
            func.avg(Assessment.stress_level)
        )
        .filter_by(user_id=identity)
        .scalar()
    )

    avg_mood = (
        Assessment.query.with_entities(
            func.avg(Assessment.mood)
        )
        .filter_by(user_id=identity)
        .scalar()
    )

    avg_energy = (
        Assessment.query.with_entities(
            func.avg(Assessment.energy_level)
        )
        .filter_by(user_id=identity)
        .scalar()
    )

    # Latest Risk
    latest_risk = latest_assessment.prediction_score * 100

    # Risk Level
    if latest_risk < 30:
        risk_level = "Low"
    elif latest_risk < 70:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    # Trend Analysis
    trend = "Not Enough Data"

    if previous_assessment:

        previous_risk = previous_assessment.prediction_score * 100

        difference = latest_risk - previous_risk

        if difference >= 10:
            trend = "Declining"

        elif difference <= -10:
            trend = "Improving"

        else:
            trend = "Stable"

    return jsonify({
        "total_assessments": total_assessments,
        "latest_risk_score": round(latest_risk, 2),
        "latest_risk_level": risk_level,
        "trend": trend,
        "average_sleep": round(float(avg_sleep), 2),
        "average_stress": round(float(avg_stress), 2),
        "average_mood": round(float(avg_mood), 2),
        "average_energy": round(float(avg_energy), 2)
    }), 200