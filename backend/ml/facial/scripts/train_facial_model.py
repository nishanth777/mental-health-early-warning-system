from pathlib import Path

import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split


SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent
DATASET_DIR = ML_DIR / "dataset" / "fer2013"

TRAIN_DIR = DATASET_DIR / "train"

MODEL_DIR = ML_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "facial_emotion_cnn_v2.pth"


class FacialEmotionCNN(nn.Module):
    def __init__(self, num_classes=7):
        super().__init__()

        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.20),

            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.25),

            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.30),

            # Block 4
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.35),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),

            nn.Linear(256 * 3 * 3, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),

            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def evaluate(model, data_loader, device, criterion):
    model.eval()

    total_loss = 0.0
    correct = 0
    total_samples = 0

    with torch.no_grad():
        for images, labels in data_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            total_loss += (
                loss.item() * images.size(0)
            )

            predictions = torch.argmax(
                outputs,
                dim=1
            )

            correct += (
                (predictions == labels)
                .sum()
                .item()
            )

            total_samples += images.size(0)

    return (
        total_loss / total_samples,
        (correct / total_samples) * 100
    )


def main():
    print("FER-2013 Facial Emotion CNN v2")
    print("=" * 50)

    device = torch.device("cpu")

    print(f"Device: {device}")

    # --------------------------------------------------
    # Transforms
    # --------------------------------------------------

    train_transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.RandomAffine(
            degrees=0,
            translate=(0.10, 0.10),
            scale=(0.90, 1.10)
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.5],
            std=[0.5]
        ),
    ])

    validation_transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.5],
            std=[0.5]
        ),
    ])

    # --------------------------------------------------
    # Load full training dataset
    # --------------------------------------------------

    full_dataset = datasets.ImageFolder(
        root=TRAIN_DIR,
        transform=train_transform
    )

    # Create validation split
    validation_size = int(
        0.10 * len(full_dataset)
    )

    training_size = (
        len(full_dataset) - validation_size
    )

    generator = torch.Generator().manual_seed(42)

    train_dataset, validation_dataset = random_split(
        full_dataset,
        [training_size, validation_size],
        generator=generator
    )

    # Use non-augmented transform for validation
    validation_dataset.dataset.transform = validation_transform

    train_loader = DataLoader(
        train_dataset,
        batch_size=64,
        shuffle=True,
        num_workers=0
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=64,
        shuffle=False,
        num_workers=0
    )

    # --------------------------------------------------
    # Class weights
    # --------------------------------------------------

    original_targets = torch.tensor(
        full_dataset.targets
    )

    train_indices = train_dataset.indices

    train_targets = original_targets[
        train_indices
    ]

    class_counts = torch.bincount(
        train_targets,
        minlength=len(full_dataset.classes)
    )

    total = len(train_targets)
    num_classes = len(full_dataset.classes)

    class_weights = total / (
        num_classes * class_counts.float()
    )

    class_weights = class_weights.to(device)

    # --------------------------------------------------
    # Model
    # --------------------------------------------------

    model = FacialEmotionCNN(
        num_classes=num_classes
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        weight=class_weights,
        label_smoothing=0.1
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=0.001,
        weight_decay=1e-4
    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=2
    )

    epochs = 15

    best_validation_accuracy = 0.0

    print()
    print(f"Total training images : {len(full_dataset)}")
    print(f"Training split        : {len(train_dataset)}")
    print(f"Validation split      : {len(validation_dataset)}")
    print(f"Classes               : {full_dataset.classes}")
    print(f"Epochs                : {epochs}")
    print(f"Batch size            : 64")
    print()
    print("Starting improved CNN training...")
    print()

    # --------------------------------------------------
    # Training
    # --------------------------------------------------

    for epoch in range(epochs):

        model.train()

        running_loss = 0.0
        correct = 0
        total_samples = 0

        for images, labels in train_loader:

            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            loss.backward()

            optimizer.step()

            running_loss += (
                loss.item() * images.size(0)
            )

            predictions = torch.argmax(
                outputs,
                dim=1
            )

            correct += (
                (predictions == labels)
                .sum()
                .item()
            )

            total_samples += images.size(0)

        train_loss = (
            running_loss / total_samples
        )

        train_accuracy = (
            correct / total_samples
        ) * 100

        validation_loss, validation_accuracy = evaluate(
            model,
            validation_loader,
            device,
            criterion
        )

        scheduler.step(validation_loss)

        current_lr = optimizer.param_groups[0]["lr"]

        print(
            f"Epoch {epoch + 1:02d}/{epochs} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Train Acc: {train_accuracy:.2f}% | "
            f"Val Loss: {validation_loss:.4f} | "
            f"Val Acc: {validation_accuracy:.2f}% | "
            f"LR: {current_lr:.6f}"
        )

        if validation_accuracy > best_validation_accuracy:

            best_validation_accuracy = (
                validation_accuracy
            )

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "classes": full_dataset.classes,
                    "validation_accuracy": (
                        validation_accuracy
                    ),
                },
                MODEL_PATH
            )

            print(
                f"  ✓ Best v2 model saved "
                f"({validation_accuracy:.2f}%)"
            )

    print()
    print("=" * 50)
    print("IMPROVED CNN TRAINING COMPLETE")
    print("=" * 50)
    print(
        f"Best Validation Accuracy: "
        f"{best_validation_accuracy:.2f}%"
    )
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()