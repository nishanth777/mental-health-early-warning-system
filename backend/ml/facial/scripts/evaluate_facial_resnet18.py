from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import resnet18

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TEST_DIR = BASE_DIR / "dataset" / "fer2013" / "test"

# IMPORTANT: Evaluate the fine-tuned model, not frozen ResNet18.
MODEL_PATH = (
    BASE_DIR
    / "models"
    / "facial_emotion_resnet18_finetuned.pth"
)

IMAGE_SIZE = 112
BATCH_SIZE = 64

DEVICE = torch.device("cpu")

EMOTION_CLASSES = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
]


# ============================================================
# VALIDATE PATHS
# ============================================================

if not TEST_DIR.exists():
    raise FileNotFoundError(
        f"FER-2013 test directory not found: {TEST_DIR}"
    )

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Fine-tuned model not found: {MODEL_PATH}"
    )


# ============================================================
# TRANSFORM
# ============================================================

test_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),

    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])


# ============================================================
# LOAD OFFICIAL TEST DATASET
# ============================================================

test_dataset = datasets.ImageFolder(
    TEST_DIR,
    transform=test_transform
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


print("=" * 65)
print("FER-2013 FINE-TUNED RESNET18 - OFFICIAL TEST EVALUATION")
print("=" * 65)

print(f"Test directory : {TEST_DIR}")
print(f"Test images    : {len(test_dataset)}")
print(f"Device         : {DEVICE}")
print("=" * 65)


# ============================================================
# VERIFY CLASS ORDER
# ============================================================

if test_dataset.classes != EMOTION_CLASSES:
    raise ValueError(
        "\nEmotion class order mismatch!\n"
        f"Expected: {EMOTION_CLASSES}\n"
        f"Found:    {test_dataset.classes}\n"
        "Check the FER-2013 dataset folders before continuing."
    )


# ============================================================
# LOAD FINE-TUNED RESNET18
# ============================================================

print("\nLoading fine-tuned ResNet18...")

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE,
    weights_only=True
)

checkpoint_classes = checkpoint.get("classes")

if checkpoint_classes != EMOTION_CLASSES:
    raise ValueError(
        "\nCheckpoint class order mismatch!\n"
        f"Expected: {EMOTION_CLASSES}\n"
        f"Found:    {checkpoint_classes}"
    )

checkpoint_image_size = checkpoint.get("image_size")

if checkpoint_image_size != IMAGE_SIZE:
    raise ValueError(
        f"Image size mismatch: checkpoint uses "
        f"{checkpoint_image_size}, evaluator uses {IMAGE_SIZE}."
    )

model = resnet18(
    weights=None,
    num_classes=len(EMOTION_CLASSES)
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)

model.eval()


# ============================================================
# DISPLAY CHECKPOINT INFORMATION
# ============================================================

print("\nModel loaded successfully.")

print(
    "Model name:",
    checkpoint.get("model_name", "Unknown")
)

best_val_accuracy = checkpoint.get(
    "best_val_accuracy"
)

if best_val_accuracy is not None:
    print(
        "Best validation accuracy:",
        f"{best_val_accuracy * 100:.2f}%"
    )

print(f"Model path: {MODEL_PATH}")

print("\nStarting evaluation on the official test set...")


# ============================================================
# GENERATE PREDICTIONS
# ============================================================

all_predictions = []
all_labels = []

with torch.no_grad():

    for batch_number, (images, labels) in enumerate(
        test_loader,
        start=1
    ):

        images = images.to(DEVICE)

        outputs = model(images)

        predictions = torch.argmax(
            outputs,
            dim=1
        )

        all_predictions.extend(
            predictions.cpu().tolist()
        )

        all_labels.extend(
            labels.tolist()
        )

        if batch_number % 20 == 0:
            print(
                f"Processed "
                f"{len(all_predictions)}/{len(test_dataset)} images"
            )


# ============================================================
# CALCULATE METRICS
# ============================================================

accuracy = accuracy_score(
    all_labels,
    all_predictions
)

macro_f1 = f1_score(
    all_labels,
    all_predictions,
    labels=list(range(len(EMOTION_CLASSES))),
    average="macro",
    zero_division=0
)

weighted_f1 = f1_score(
    all_labels,
    all_predictions,
    labels=list(range(len(EMOTION_CLASSES))),
    average="weighted",
    zero_division=0
)


# ============================================================
# DISPLAY OVERALL RESULTS
# ============================================================

print("\n" + "=" * 65)
print("OFFICIAL TEST RESULTS")
print("=" * 65)

print(f"Accuracy    : {accuracy * 100:.2f}%")
print(f"Macro F1    : {macro_f1:.4f}")
print(f"Weighted F1 : {weighted_f1:.4f}")

print(f"Correct predictions: {sum(p == y for p, y in zip(all_predictions, all_labels))}")
print(f"Total test images  : {len(all_labels)}")


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 65)
print("PER-CLASS CLASSIFICATION REPORT")
print("=" * 65)

report = classification_report(
    all_labels,
    all_predictions,
    labels=list(range(len(EMOTION_CLASSES))),
    target_names=EMOTION_CLASSES,
    digits=4,
    zero_division=0
)

print(report)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("=" * 65)
print("CONFUSION MATRIX")
print("=" * 65)

matrix = confusion_matrix(
    all_labels,
    all_predictions,
    labels=list(range(len(EMOTION_CLASSES)))
)

print("\nClass order:")
print(EMOTION_CLASSES)

print("\nRows = Actual emotions")
print("Columns = Predicted emotions\n")

print(matrix)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 65)
print("EVALUATION COMPLETE")
print("=" * 65)

print("Model: Fine-tuned ResNet18")
print(f"Official test accuracy: {accuracy * 100:.2f}%")
print(f"Macro F1-score: {macro_f1:.4f}")
print(f"Weighted F1-score: {weighted_f1:.4f}")

print("\nNo training or model modification was performed.")
print("=" * 65)