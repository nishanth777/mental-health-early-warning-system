import joblib
from pathlib import Path


# ============================================================
# Load model
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "nlp_model.pkl"
)

model = joblib.load(MODEL_PATH)


# ============================================================
# Test journal entries
# ============================================================

test_entries = [
    # Lower concern
    "I went to class today and finished my assignment. Feeling pretty normal.",

    "I had a productive day and managed to complete most of my work.",

    "I spent some time with my friends and relaxed after college.",

    # Elevated concern
    "I couldn't focus on anything today and kept worrying about college.",

    "I feel exhausted and I am struggling to keep up with everything.",

    "My thoughts have been racing and I have been finding it difficult to relax.",

    # Ambiguous / mixed
    "College was tiring today but I managed to finish most of my work.",

    "I was stressed about my exam but I took a break and felt better later.",

    # Neutral
    "I attended three lectures and worked on my project afterwards.",

    # Low-information
    "the the the the the",
]


# ============================================================
# Prediction
# ============================================================

print("=" * 70)
print("NLP MODEL MANUAL TEST")
print("=" * 70)

for i, text in enumerate(test_entries, start=1):

    prediction = int(model.predict([text])[0])

    probability = float(
        model.predict_proba([text])[0][1]
    )

    if prediction == 1:
        label = "Elevated Concern"
    else:
        label = "Lower Concern"

    print(f"\nTest {i}")
    print("-" * 70)
    print("Text:", text)
    print("Prediction:", label)
    print(
        "Elevated concern probability:",
        round(probability, 4)
    )