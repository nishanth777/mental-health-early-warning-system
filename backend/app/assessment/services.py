from functools import lru_cache
from pathlib import Path
import csv

import joblib


# --------------------------------------------------
# PATHS
# --------------------------------------------------

# Path to backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Trained structured ML model
MODEL_PATH = BASE_DIR / "ml" / "models" / "depression_model.pkl"

# Dataset used for training the structured model
DATASET_PATH = BASE_DIR / "ml" / "dataset" / "synthetic_assessment_dataset.csv"


# --------------------------------------------------
# FEATURE DEFINITIONS
# --------------------------------------------------

FEATURE_NAMES = [
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
]

FEATURE_LABELS = {
    "sleep_hours": "Sleep duration",
    "sleep_quality": "Sleep quality",
    "stress_level": "Stress level",
    "academic_pressure": "Academic pressure",
    "mood": "Mood",
    "energy_level": "Energy level",
    "social_interaction": "Social interaction",
    "exercise_minutes": "Physical activity",
    "screen_time": "Screen time",
    "study_hours": "Study hours",
}


# --------------------------------------------------
# MODEL LOADING
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_model():
    """Load the structured ML model once, when first needed."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Depression model file not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    print("Structured ML model loaded successfully.")

    return model


# --------------------------------------------------
# TRAINING DATA BASELINE
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_feature_baselines():
    """
    Calculate the mean value of every model feature
    from the structured training dataset.

    These means are used as the reference point
    for the explainability calculations.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATASET_PATH}"
        )

    totals = {feature: 0.0 for feature in FEATURE_NAMES}
    counts = {feature: 0 for feature in FEATURE_NAMES}

    with open(DATASET_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise RuntimeError(
                "The training dataset has no column headers."
            )

        missing_features = [
            feature
            for feature in FEATURE_NAMES
            if feature not in reader.fieldnames
        ]

        if missing_features:
            raise RuntimeError(
                f"Training dataset is missing features: {missing_features}"
            )

        for row in reader:
            for feature in FEATURE_NAMES:
                try:
                    value = float(row[feature])
                except (TypeError, ValueError):
                    continue

                totals[feature] += value
                counts[feature] += 1

    baselines = {}

    for feature in FEATURE_NAMES:
        if counts[feature] == 0:
            raise RuntimeError(
                f"No valid training values found for feature: {feature}"
            )

        baselines[feature] = totals[feature] / counts[feature]

    return baselines


# --------------------------------------------------
# STRUCTURED ML PREDICTION
# --------------------------------------------------

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

    model = get_model()

    prediction = int(model.predict(features)[0])
    risk_score = float(model.predict_proba(features)[0][1])

    return prediction, risk_score


# --------------------------------------------------
# EXPLAINABLE AI
# --------------------------------------------------

def explain_structured_prediction(assessment_data):
    """
    Explain how each input feature influences the
    structured Logistic Regression model's estimated risk.

    Uses coefficient-based feature attribution:

        contribution = coefficient * (input - baseline)

    Contributions are expressed in log-odds, NOT percentages.

    Positive contribution:
        Moves the model toward class 1 (higher concern).

    Negative contribution:
        Moves the model away from class 1 (lower concern).

    These explanations describe model behavior.
    They do not establish clinical causes.
    """

    model = get_model()

    # Ensure the model supports coefficient-based explanations.
    if not hasattr(model, "coef_") or not hasattr(model, "classes_"):
        raise RuntimeError(
            "The current model does not support coefficient-based explanations."
        )

    if len(model.classes_) != 2 or 1 not in model.classes_:
        raise RuntimeError(
            "Explainability currently supports binary classification "
            "with class 1 representing higher concern."
        )

    # Verify feature count.
    coefficients = model.coef_[0]

    if len(coefficients) != len(FEATURE_NAMES):
        raise RuntimeError(
            "Model feature count does not match the expected feature list."
        )

    # Verify feature names and ordering when available.
    if hasattr(model, "feature_names_in_"):
        model_features = list(model.feature_names_in_)

        if model_features != FEATURE_NAMES:
            raise RuntimeError(
                "Model feature names or ordering do not match "
                "the expected feature definitions."
            )

    # Load average training values.
    baselines = get_feature_baselines()

    explanations = []

    for index, feature in enumerate(FEATURE_NAMES):

        input_value = float(assessment_data[feature])
        baseline_value = float(baselines[feature])
        coefficient = float(coefficients[index])

        # Feature contribution to the class-1 logit,
        # relative to the training-data mean.
        contribution = coefficient * (
            input_value - baseline_value
        )

        if contribution > 1e-9:
            direction = "increases_concern"

        elif contribution < -1e-9:
            direction = "decreases_concern"

        else:
            direction = "neutral"

        explanations.append({
            "feature": feature,
            "label": FEATURE_LABELS[feature],
            "value": round(input_value, 2),
            "baseline_value": round(baseline_value, 2),
            "contribution": round(contribution, 6),
            "direction": direction,
        })

    # Show the strongest model contributions first.
    explanations.sort(
        key=lambda item: abs(item["contribution"]),
        reverse=True
    )

    increasing_factors = [
        item for item in explanations
        if item["direction"] == "increases_concern"
    ]

    decreasing_factors = [
        item for item in explanations
        if item["direction"] == "decreases_concern"
    ]

    neutral_factors = [
        item for item in explanations
        if item["direction"] == "neutral"
    ]

    return {
        "method": "logistic_regression_coefficient_attribution",

        "baseline_source": "training_dataset_mean",

        "increasing_factors": increasing_factors,

        "decreasing_factors": decreasing_factors,

        "neutral_factors": neutral_factors,

        "all_factors": explanations,

        "note": (
            "These contributions describe how the structured "
            "machine learning model uses each input relative to "
            "the training dataset averages. They are expressed "
            "in log-odds, not percentages. They are not clinical "
            "evidence and do not establish causes of mental "
            "health conditions. This explanation applies only "
            "to the structured model, not the final multimodal "
            "risk score."
        ),
    }


# --------------------------------------------------
# RISK CLASSIFICATION
# --------------------------------------------------

def get_risk_level(risk_score):
    """Convert probability into a human-readable risk level."""

    percentage = risk_score * 100

    if percentage < 30:
        return "Low"

    elif percentage < 70:
        return "Moderate"

    else:
        return "High"


# --------------------------------------------------
# RECOMMENDATIONS
# --------------------------------------------------

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

    if not recommendations:
        recommendations.append(
            "Keep maintaining your healthy lifestyle."
        )

    return recommendations