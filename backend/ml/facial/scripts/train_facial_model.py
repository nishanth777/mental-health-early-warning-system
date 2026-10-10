from pathlib import Path

import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import numpy as np


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent

DATASET_DIR = ML_DIR / "dataset" / "fer2013"
TRAIN_DIR = DATASET_DIR / "train"

MODEL_DIR = ML_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "facial_emotion_cnn_v4.pth"


# ============================================================
# SETTINGS
# ============================================================

BATCH_SIZE = 64
EPOCHS = 25
LEARNING_RATE = 0.001
RANDOM_STATE = 42

# Focal Loss parameters
FOCAL_GAMMA = 2.0


# ============================================================
# DEVICE
# ============================================================

device = torch.device("cpu")

print("Device:", device)


# ============================================================
# TRAINING TRANSFORM
# ============================================================

train_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),

    transforms.RandomHorizontalFlip(p=0.5),

    transforms.RandomRotation(
        degrees=10
    ),

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


# ============================================================
# VALIDATION TRANSFORM
# ============================================================

validation_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.5],
        std=[0.5]
    ),
])


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("Loading FER-2013 training dataset...")

full_dataset = datasets.ImageFolder(
    root=TRAIN_DIR,
    transform=train_transform
)

print(
    "Total images:",
    len(full_dataset)
)

print(
    "Classes:",
    full_dataset.classes
)


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

targets = np.array(
    full_dataset.targets
)

indices = np.arange(
    len(full_dataset)
)

train_indices, validation_indices = train_test_split(
    indices,
    test_size=0.10,
    random_state=RANDOM_STATE,
    stratify=targets
)


# ============================================================
# VALIDATION DATASET
# ============================================================

validation_dataset_full = datasets.ImageFolder(
    root=TRAIN_DIR,
    transform=validation_transform
)


# ============================================================
# CLASS INFORMATION
# ============================================================

class_names = full_dataset.classes

num_classes = len(
    class_names
)

train_targets = targets[
    train_indices
]


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

class_counts = np.bincount(
    train_targets,
    minlength=num_classes
)

print()
print("Training class distribution:")

for index, class_name in enumerate(
    class_names
):

    print(
        f"{class_name:10s}: "
        f"{class_counts[index]}"
    )


# ============================================================
# DATASETS
# ============================================================

train_subset = torch.utils.data.Subset(
    full_dataset,
    train_indices
)

validation_subset = torch.utils.data.Subset(
    validation_dataset_full,
    validation_indices
)


# ============================================================
# DATALOADERS
# ============================================================

train_loader = DataLoader(
    train_subset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

validation_loader = DataLoader(
    validation_subset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# ============================================================
# CNN MODEL
# ============================================================

class FacialEmotionCNN(nn.Module):

    def __init__(self, num_classes=7):

        super().__init__()

        self.features = nn.Sequential(

            # ------------------------------------------------
            # Block 1
            # ------------------------------------------------

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


            # ------------------------------------------------
            # Block 2
            # ------------------------------------------------

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


            # ------------------------------------------------
            # Block 3
            # ------------------------------------------------

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


            # ------------------------------------------------
            # Block 4
            # ------------------------------------------------

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


# ============================================================
# FOCAL LOSS
# ============================================================

class FocalLoss(nn.Module):

    def __init__(
        self,
        gamma=2.0,
        alpha=None
    ):

        super().__init__()

        self.gamma = gamma
        self.alpha = alpha


    def forward(
        self,
        logits,
        targets
    ):

        log_probs = torch.log_softmax(
            logits,
            dim=1
        )

        probs = torch.exp(
            log_probs
        )

        target_log_probs = log_probs[
            torch.arange(
                logits.size(0),
                device=logits.device
            ),
            targets
        ]

        target_probs = probs[
            torch.arange(
                logits.size(0),
                device=logits.device
            ),
            targets
        ]


        focal_factor = (
            1.0 - target_probs
        ) ** self.gamma


        loss = (
            -focal_factor
            * target_log_probs
        )


        # Optional class weighting
        if self.alpha is not None:

            alpha_factor = self.alpha[
                targets
            ]

            loss = (
                alpha_factor
                * loss
            )


        return loss.mean()


# ============================================================
# CLASS WEIGHTS
# ============================================================

class_weights = (
    len(train_targets)
    /
    (
        num_classes
        * class_counts
    )
)

class_weights_tensor = torch.tensor(
    class_weights,
    dtype=torch.float32
).to(device)


# ============================================================
# CREATE MODEL
# ============================================================

model = FacialEmotionCNN(
    num_classes=num_classes
).to(device)


# ============================================================
# LOSS
# ============================================================

criterion = FocalLoss(
    gamma=FOCAL_GAMMA,
    alpha=class_weights_tensor
)


# ============================================================
# OPTIMIZER
# ============================================================

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=1e-4
)


# ============================================================
# LEARNING RATE SCHEDULER
# ============================================================

scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="max",
    factor=0.5,
    patience=2
)


# ============================================================
# BEST MODEL
# ============================================================

best_validation_accuracy = 0.0

best_epoch = 0


# ============================================================
# TRAINING LOOP
# ============================================================

for epoch in range(EPOCHS):

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    model.train()

    running_loss = 0.0

    correct = 0

    total = 0


    for images, labels in train_loader:

        images = images.to(device)

        labels = labels.to(device)


        optimizer.zero_grad()


        outputs = model(
            images
        )


        loss = criterion(
            outputs,
            labels
        )


        loss.backward()


        optimizer.step()


        running_loss += (
            loss.item()
            * images.size(0)
        )


        predictions = torch.argmax(
            outputs,
            dim=1
        )


        total += labels.size(0)


        correct += (
            predictions == labels
        ).sum().item()


    train_loss = (
        running_loss
        / total
    )


    train_accuracy = (
        correct
        / total
    ) * 100


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    model.eval()

    validation_correct = 0

    validation_total = 0

    validation_loss_total = 0.0


    with torch.no_grad():

        for images, labels in validation_loader:

            images = images.to(device)

            labels = labels.to(device)


            outputs = model(
                images
            )


            loss = criterion(
                outputs,
                labels
            )


            validation_loss_total += (
                loss.item()
                * images.size(0)
            )


            predictions = torch.argmax(
                outputs,
                dim=1
            )


            validation_total += (
                labels.size(0)
            )


            validation_correct += (
                predictions == labels
            ).sum().item()


    validation_loss = (
        validation_loss_total
        / validation_total
    )


    validation_accuracy = (
        validation_correct
        / validation_total
    ) * 100


    # --------------------------------------------------------
    # LEARNING RATE
    # --------------------------------------------------------

    scheduler.step(
        validation_accuracy
    )


    current_lr = (
        optimizer.param_groups[0]["lr"]
    )


    # --------------------------------------------------------
    # SAVE BEST MODEL
    # --------------------------------------------------------

    if (
        validation_accuracy
        > best_validation_accuracy
    ):

        best_validation_accuracy = (
            validation_accuracy
        )

        best_epoch = epoch + 1


        torch.save(
            {
                "model_state_dict":
                    model.state_dict(),

                "val_accuracy":
                    validation_accuracy,

                "val_loss":
                    validation_loss,

                "epoch":
                    epoch + 1,

                "classes":
                    class_names,
            },
            MODEL_PATH
        )


    # --------------------------------------------------------
    # PRINT
    # --------------------------------------------------------

    print(
        f"Epoch [{epoch + 1}/{EPOCHS}] "
        f"Train Loss: {train_loss:.4f} "
        f"Train Acc: {train_accuracy:.2f}% "
        f"Val Loss: {validation_loss:.4f} "
        f"Val Acc: {validation_accuracy:.2f}% "
        f"LR: {current_lr:.6f}"
    )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 60)

print(
    "V4 training completed."
)

print(
    f"Best validation accuracy: "
    f"{best_validation_accuracy:.2f}%"
)

print(
    f"Best epoch: {best_epoch}"
)

print(
    f"Model saved to: {MODEL_PATH}"
)

print("=" * 60)