import joblib
import pandas as pd

from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR
    / "dataset"
    / "synthetic_nlp_dataset.csv"
)

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "nlp_model.pkl"
)


# ============================================================
# Load dataset
# ============================================================

print("Loading NLP dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Dataset shape: {df.shape}")

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# Basic validation
# ============================================================

if "text" not in df.columns or "label" not in df.columns:
    raise ValueError(
        "Dataset must contain 'text' and 'label' columns."
    )

df = df.dropna(subset=["text", "label"])

df["text"] = df["text"].astype(str)

print("\nLabel distribution:")
print(df["label"].value_counts())


# ============================================================
# Features and target
# ============================================================

X = df["text"]
y = df["label"]


# ============================================================
# Train / Test split
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nTrain samples:", len(X_train))
print("Test samples:", len(X_test))


# ============================================================
# TF-IDF + Logistic Regression Pipeline
# ============================================================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            min_df=2,
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            random_state=42,
        )
    ),
])


# ============================================================
# Training
# ============================================================

print("\nTraining NLP model...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# Predictions
# ============================================================

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# ============================================================
# Evaluation
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)

print("\n" + "=" * 60)
print("NLP MODEL EVALUATION")
print("=" * 60)

print(
    f"\nAccuracy: {accuracy:.4f}"
    f" ({accuracy * 100:.2f}%)"
)

print(
    f"ROC-AUC: {roc_auc:.4f}"
)


print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Lower Concern",
            "Elevated Concern"
        ]
    )
)


print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# Save model
# ============================================================

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print("\n" + "=" * 60)
print("MODEL SAVED")
print("=" * 60)

print(f"\nSaved to:")
print(MODEL_PATH)


# ============================================================
# Reload test
# ============================================================

loaded_model = joblib.load(
    MODEL_PATH
)

test_prediction = loaded_model.predict(
    ["I have been struggling to concentrate on my studies lately."]
)

test_probability = loaded_model.predict_proba(
    ["I have been struggling to concentrate on my studies lately."]
)[0][1]

print("\nReload test:")
print("Prediction:", int(test_prediction[0]))
print(
    "Elevated concern probability:",
    round(float(test_probability), 4)
)