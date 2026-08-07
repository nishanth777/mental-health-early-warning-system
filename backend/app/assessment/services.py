import joblib
from pathlib import Path

# Path to backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Path to trained ML model
MODEL_PATH = BASE_DIR / "ml" / "models" / "depression_model.pkl"

# Load model once when Flask starts
model = joblib.load(MODEL_PATH)

print("✅ ML Model Loaded Successfully")
print(model)


def predict_depression(assessment_data):
    """
    Predict depression risk based on assessment data.

    Returns:
        prediction (int): 0 = Low Risk, 1 = High Risk
        risk_score (float): Probability between 0 and 1
    """

    features = [[
        assessment_data["sleep_hours"],
        assessment_data["sleep_quality"],
        assessment_data["stress_level"],
        assessment_data["academic_pressure"],
        assessment_data["mood"],
        assessment_data["energy_level"],
        assessment_data["social_interaction"],
        assessment_data["exercise_minutes"],
        assessment_data["screen_time"],
        assessment_data["study_hours"],
    ]]

    prediction = int(model.predict(features)[0])

    risk_score = float(model.predict_proba(features)[0][1])

    return prediction, risk_score
def get_risk_level(risk_score):
    """
    Convert probability into a human-readable risk level.
    """

    percentage = risk_score * 100

    if percentage < 30:
        return "Low"

    elif percentage < 70:
        return "Moderate"

    else:
        return "High"

def generate_recommendations(assessment_data, risk_score):

    recommendations = []

    if assessment_data["sleep_hours"] < 7:
        recommendations.append(
            "Try to get at least 7-8 hours of sleep every night."
        )

    if assessment_data["exercise_minutes"] < 30:
        recommendations.append(
            "Aim for at least 30 minutes of physical activity daily."
        )

    if assessment_data["screen_time"] > 8:
        recommendations.append(
            "Reduce screen time, especially before bedtime."
        )

    if assessment_data["stress_level"] >= 4:
        recommendations.append(
            "Practice stress management techniques like meditation or deep breathing."
        )

    if assessment_data["mood"] <= 2:
        recommendations.append(
            "Talk to someone you trust about how you're feeling."
        )

    if assessment_data["social_interaction"] <= 2:
        recommendations.append(
            "Spend more time connecting with friends or family."
        )

    if risk_score >= 0.70:
        recommendations.append(
            "Consider consulting a mental health professional if these feelings continue."
        )

    if len(recommendations) == 0:
        recommendations.append(
            "Keep maintaining your healthy lifestyle."
        )

    return recommendations