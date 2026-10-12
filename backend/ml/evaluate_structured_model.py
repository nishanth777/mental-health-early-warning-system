from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "dataset" / "synthetic_assessment_dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "depression_model.pkl"

# Load the existing dataset and saved model.
df = pd.read_csv(DATASET_PATH)
model = joblib.load(MODEL_PATH)

X = df.drop(columns=["depression"])
y = df["depression"]

# Reproduce the notebook's original split.
_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# Evaluate the saved model without retraining.
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("=" * 60)
print("STRUCTURED MODEL EVALUATION")
print("=" * 60)

print(f"Dataset samples: {len(df)}")
print(f"Test samples: {len(y_test)}")

print(f"\nAccuracy: {accuracy_score(y_test, predictions) * 100:.2f}%")
print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=["Class 0", "Class 1"],
        digits=4,
        zero_division=0,
    )
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nEvaluation complete.")
print("No training or model modification was performed.")