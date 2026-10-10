from pathlib import Path

import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent

DATASET_DIR = ML_DIR / "dataset" / "fer2013"
TEST_DIR = DATASET_DIR / "test"

MODEL_PATH = (
    ML_DIR
    / "models"
    / "facial_emotion_cnn_v2.pth"
)


# ------------------------------------------------------------
# CNN architecture - V2
# ------------------------------------------------------------

class FacialEmotionCNN(nn.Module):

    def __init__(self, num_classes=7):
        super().__init__()

        self.features = nn.Sequential(

            # Block 1
            nn.Conv2d(
                1,
                32,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                32,
                32,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.20),

            # Block 2
            nn.Conv2d(
                32,
                64,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                64,
                64,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.25),

            # Block 3
            nn.Conv2d(
                64,
                128,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                128,
                128,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.30),

            # Block 4
            nn.Conv2d(
                128,
                256,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.35),
        )

        self.classifier = nn.Sequential(

            nn.Flatten(),

            nn.Linear(
                256 * 3 * 3,
                256
            ),

            nn.ReLU(inplace=True),

            nn.Dropout(0.5),

            nn.Linear(
                256,
                num_classes
            )
        )

    def forward(self, x):

        x = self.features(x)

        x = self.classifier(x)

        return x


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("FER-2013 Facial Emotion Evaluation - V2")
    print("=" * 55)

    device = torch.device("cpu")

    # --------------------------------------------------------
    # Test preprocessing
    # --------------------------------------------------------

    test_transform = transforms.Compose([
        transforms.Grayscale(
            num_output_channels=1
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.5],
            std=[0.5]
        ),
    ])

    # --------------------------------------------------------
    # Load official FER-2013 test set
    # --------------------------------------------------------

    test_dataset = datasets.ImageFolder(
        root=TEST_DIR,
        transform=test_transform
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=64,
        shuffle=False,
        num_workers=0
    )

    print()
    print("Test samples:", len(test_dataset))
    print("Classes:", test_dataset.classes)

    # --------------------------------------------------------
    # Load V2 model
    # --------------------------------------------------------

    model = FacialEmotionCNN(
        num_classes=len(test_dataset.classes)
    ).to(device)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    all_predictions = []
    all_labels = []

    with torch.no_grad():

        for images, labels in test_loader:

            images = images.to(device)

            outputs = model(images)

            predictions = torch.argmax(
                outputs,
                dim=1
            )

            all_predictions.extend(
                predictions.cpu().numpy()
            )

            all_labels.extend(
                labels.numpy()
            )

    # --------------------------------------------------------
    # Accuracy stored during training
    # --------------------------------------------------------

    print()
    print(
        "Best validation accuracy saved during training: "
        f"{checkpoint.get('val_accuracy', 0):.2f}%"
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    print()
    print("Classification Report")
    print("=" * 55)

    report = classification_report(
        all_labels,
        all_predictions,
        target_names=test_dataset.classes,
        digits=4,
        zero_division=0
    )

    print(report)

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    print("Confusion Matrix")
    print("=" * 55)

    matrix = confusion_matrix(
        all_labels,
        all_predictions
    )

    print(matrix)

    print()
    print("Evaluation completed successfully.")


if __name__ == "__main__":
    main()