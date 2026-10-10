from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = BASE_DIR / "dataset" / "fer2013"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "facial_emotion_resnet18.pth"

EMOTION_CLASSES = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
]

NUM_CLASSES = 7

IMAGE_SIZE = 112
BATCH_SIZE = 64
EPOCHS = 15

VAL_SPLIT = 0.10
RANDOM_SEED = 42

DEVICE = torch.device("cpu")

torch.manual_seed(RANDOM_SEED)


# ============================================================
# TRANSFORMS
# ============================================================

train_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),

    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.RandomHorizontalFlip(p=0.5),

    transforms.RandomRotation(10),

    transforms.RandomAffine(
        degrees=0,
        translate=(0.10, 0.10),
        scale=(0.90, 1.10)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])


validation_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),

    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])


# ============================================================
# DATASET
# ============================================================

full_dataset = datasets.ImageFolder(
    DATASET_DIR / "train",
    transform=train_transform
)

dataset_size = len(full_dataset)

val_size = int(dataset_size * VAL_SPLIT)
train_size = dataset_size - val_size

generator = torch.Generator().manual_seed(RANDOM_SEED)

train_dataset, val_dataset = random_split(
    full_dataset,
    [train_size, val_size],
    generator=generator
)

# Validation must not use augmentation
val_dataset.dataset = datasets.ImageFolder(
    DATASET_DIR / "train",
    transform=validation_transform
)

# Re-create the exact validation indices
_, validation_indices = random_split(
    range(dataset_size),
    [train_size, val_size],
    generator=torch.Generator().manual_seed(RANDOM_SEED)
)

val_dataset = torch.utils.data.Subset(
    val_dataset.dataset,
    validation_indices.indices
)


print("=" * 60)
print("FER-2013 ResNet18 - CPU FRIENDLY TRAINING")
print("=" * 60)

print(f"Dataset directory : {DATASET_DIR}")
print(f"Total images      : {dataset_size}")
print(f"Training images   : {train_size}")
print(f"Validation images : {val_size}")
print(f"Image size        : {IMAGE_SIZE}x{IMAGE_SIZE}")
print(f"Batch size        : {BATCH_SIZE}")
print(f"Epochs            : {EPOCHS}")
print(f"Device            : {DEVICE}")
print("=" * 60)


# ============================================================
# DATALOADERS
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# ============================================================
# LOAD PRETRAINED RESNET18
# ============================================================

print("\nLoading pretrained ResNet18...")

weights = ResNet18_Weights.DEFAULT

model = resnet18(weights=weights)


# ============================================================
# FREEZE BACKBONE
# ============================================================

for parameter in model.parameters():
    parameter.requires_grad = False


# Replace final classifier
model.fc = nn.Linear(
    model.fc.in_features,
    NUM_CLASSES
)

model = model.to(DEVICE)

print("ResNet18 loaded.")
print("Backbone frozen.")
print("Only final classifier will be trained.")


# ============================================================
# CLASS WEIGHTS
# ============================================================

class_counts = [0] * NUM_CLASSES

for _, label in train_dataset:
    class_counts[label] += 1

total_samples = sum(class_counts)

class_weights = [
    total_samples / (NUM_CLASSES * count)
    for count in class_counts
]

class_weights = torch.tensor(
    class_weights,
    dtype=torch.float32
).to(DEVICE)


print("\nClass counts:")

for class_name, count in zip(
    EMOTION_CLASSES,
    class_counts
):
    print(
        f"{class_name:10s}: {count}"
    )


print("\nClass weights:")

for class_name, weight in zip(
    EMOTION_CLASSES,
    class_weights
):
    print(
        f"{class_name:10s}: {weight.item():.4f}"
    )


# ============================================================
# LOSS
# ============================================================

criterion = nn.CrossEntropyLoss(
    weight=class_weights,
    label_smoothing=0.1
)


# ============================================================
# OPTIMIZER
# ============================================================

optimizer = torch.optim.AdamW(
    model.fc.parameters(),
    lr=0.001,
    weight_decay=1e-4
)


# ============================================================
# TRAIN
# ============================================================

def train_one_epoch():

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

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
            predictions == labels
        ).sum().item()

        total += labels.size(0)

    loss = running_loss / total
    accuracy = correct / total

    return loss, accuracy


# ============================================================
# VALIDATION
# ============================================================

def validate():

    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            running_loss += (
                loss.item() * images.size(0)
            )

            predictions = torch.argmax(
                outputs,
                dim=1
            )

            correct += (
                predictions == labels
            ).sum().item()

            total += labels.size(0)

    loss = running_loss / total
    accuracy = correct / total

    return loss, accuracy


# ============================================================
# TRAINING LOOP
# ============================================================

best_val_accuracy = 0.0

print("\nStarting training...")
print("=" * 60)


for epoch in range(EPOCHS):

    train_loss, train_accuracy = (
        train_one_epoch()
    )

    val_loss, val_accuracy = validate()

    print(
        f"Epoch [{epoch + 1:02d}/{EPOCHS}] "
        f"| Train Loss: {train_loss:.4f} "
        f"| Train Acc: {train_accuracy * 100:.2f}% "
        f"| Val Loss: {val_loss:.4f} "
        f"| Val Acc: {val_accuracy * 100:.2f}%"
    )

    if val_accuracy > best_val_accuracy:

        best_val_accuracy = val_accuracy

        torch.save(
            {
                "model_state_dict":
                    model.state_dict(),

                "classes":
                    EMOTION_CLASSES,

                "image_size":
                    IMAGE_SIZE,

                "best_val_accuracy":
                    best_val_accuracy,

                "model_name":
                    "ResNet18"
            },
            MODEL_PATH
        )

        print(
            f"  ✓ Best model saved "
            f"({best_val_accuracy * 100:.2f}%)"
        )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)

print(
    f"Best validation accuracy: "
    f"{best_val_accuracy * 100:.2f}%"
)

print("\nModel saved to:")

print(MODEL_PATH)

print("=" * 60)