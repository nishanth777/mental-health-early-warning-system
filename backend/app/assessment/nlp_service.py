import re
from collections import Counter
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

# ============================================================
# NLP Model
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

NLP_MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "nlp_model.pkl"
)

nlp_model = joblib.load(NLP_MODEL_PATH)

print("✅ NLP Model Loaded Successfully")
print(nlp_model)
# Common English stop words
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then",
    "is", "am", "are", "was", "were", "be", "been",
    "to", "of", "in", "on", "for", "with", "at", "by",
    "from", "as", "it", "this", "that", "these", "those",
    "i", "me", "my", "mine", "we", "our", "you", "your",
    "he", "she", "they", "them", "his", "her", "their",
    "do", "does", "did", "have", "has", "had",
    "very", "just", "so", "too",
    "about", "into", "over", "under", "after", "before",
    "again", "more", "most", "some", "such"
}


def validate_text(text):
    """
    Validate whether journal text contains enough meaningful
    information for NLP processing.
    """

    if not text or not text.strip():
        return {
            "valid": False,
            "reason": "Journal text is empty."
        }

    text = text.lower()

    # Extract alphabetic words
    words = re.findall(r"\b[a-zA-Z]+\b", text)

    if len(words) == 0:
        return {
            "valid": False,
            "reason": "No valid words found."
        }

    # Remove stop words
    meaningful_words = [
        word for word in words
        if word not in STOP_WORDS
    ]

    unique_words = set(meaningful_words)

    meaningful_count = len(meaningful_words)
    unique_count = len(unique_words)

    unique_ratio = (
        unique_count / meaningful_count
        if meaningful_count > 0
        else 0
    )

    # Repetition analysis
    word_counts = Counter(meaningful_words)

    most_common_word = None
    most_common_count = 0

    if word_counts:
        most_common_word, most_common_count = word_counts.most_common(1)[0]

    repetition_ratio = (
        most_common_count / meaningful_count
        if meaningful_count > 0
        else 0
    )

    # Minimum meaningful information
    if meaningful_count < 3:
        return {
            "valid": False,
            "reason": "Not enough meaningful words.",
            "word_count": len(words),
            "meaningful_word_count": meaningful_count,
            "unique_word_count": unique_count,
            "unique_ratio": unique_ratio,
            "repetition_ratio": repetition_ratio
        }

    # Excessive repetition
    if repetition_ratio > 0.80:
        return {
            "valid": False,
            "reason": "Excessive word repetition detected.",
            "word_count": len(words),
            "meaningful_word_count": meaningful_count,
            "unique_word_count": unique_count,
            "unique_ratio": unique_ratio,
            "repetition_ratio": repetition_ratio
        }

    return {
        "valid": True,
        "reason": "Text is suitable for NLP processing.",
        "word_count": len(words),
        "meaningful_word_count": meaningful_count,
        "unique_word_count": unique_count,
        "unique_ratio": unique_ratio,
        "repetition_ratio": repetition_ratio
    }


def preprocess_text(text):
    """
    Prepare journal text for NLP processing.

    Steps:
    1. Convert to lowercase
    2. Remove URLs
    3. Remove non-alphabetic characters
    4. Tokenize
    5. Remove stop words
    """

    if not text:
        return []

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Keep alphabetic characters only
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Tokenize
    words = text.split()

    # Remove stop words
    meaningful_words = [
        word for word in words
        if word not in STOP_WORDS
    ]

    return meaningful_words


def create_tfidf_vectorizer():
    """
    Create and return a TF-IDF vectorizer.

    The vectorizer uses the same preprocessing function
    used by the journal-processing pipeline.
    """

    return TfidfVectorizer(
        lowercase=False,
        tokenizer=lambda text: preprocess_text(text),
        token_pattern=None,
        max_features=5000
    )


def fit_tfidf(texts):
    """
    Fit a TF-IDF vectorizer on a collection of texts.

    Args:
        texts: List of journal/text documents.

    Returns:
        vectorizer: Fitted TF-IDF vectorizer
        matrix: TF-IDF feature matrix
    """

    vectorizer = create_tfidf_vectorizer()

    matrix = vectorizer.fit_transform(texts)

    return vectorizer, matrix


def transform_tfidf(vectorizer, text):
    """
    Transform a new journal entry using an already-fitted
    TF-IDF vectorizer.
    """

    return vectorizer.transform([text])

# ============================================================
# NLP Prediction
# ============================================================

def predict_nlp_risk(text):
    """
    Predict elevated concern probability from journal text.

    Returns:
        dict containing validation status, risk probability,
        and prediction.
    """

    validation = validate_text(text)

    # --------------------------------------------------------
    # Invalid / low-information text
    # --------------------------------------------------------

    if not validation["valid"]:
        return {
            "valid": False,
            "risk_score": None,
            "prediction": None,
            "reason": validation["reason"],
            "validation": validation,
        }

    # --------------------------------------------------------
    # NLP prediction
    # --------------------------------------------------------

    probability = float(
        nlp_model.predict_proba([text])[0][1]
    )

    prediction = int(
        nlp_model.predict([text])[0]
    )

    return {
        "valid": True,
        "risk_score": probability,
        "prediction": prediction,
        "reason": "Text processed successfully.",
        "validation": validation,
    }