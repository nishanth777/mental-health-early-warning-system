from pathlib import Path
import copy
import random

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights
from sklearn.metrics import f1_score, classification_report

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = BASE_DIR / "dataset" / "fer2013"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "facial_emotion_resnet18_layer3_layer4.pth"

EMOTION_CLASSES = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
NUM_CLASSES = len(EMOTION_CLASSES)
IMAGE_SIZE = 112
BATCH_SIZE = 32
EPOCHS = 12
VAL_SPLIT = 0.10
RANDOM_SEED = 42
DEVICE = torch.device("cpu")

LAYER3_LR = 0.00003
LAYER4_LR = 0.00005
CLASSIFIER_LR = 0.0003
WEIGHT_DECAY = 1e-4
LABEL_SMOOTHING = 0.05

torch.manual_seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

train_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(8),
    transforms.RandomAffine(degrees=0, translate=(0.08, 0.08), scale=(0.95, 1.05)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

eval_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

train_full = datasets.ImageFolder(DATASET_DIR / "train", transform=train_transform)
eval_full = datasets.ImageFolder(DATASET_DIR / "train", transform=eval_transform)

if train_full.classes != EMOTION_CLASSES or eval_full.classes != EMOTION_CLASSES:
    raise ValueError(f"Dataset class order mismatch. Expected {EMOTION_CLASSES}, found {train_full.classes}")

dataset_size = len(train_full)
val_size = int(dataset_size * VAL_SPLIT)
train_size = dataset_size - val_size
generator = torch.Generator().manual_seed(RANDOM_SEED)
indices = torch.randperm(dataset_size, generator=generator).tolist()
train_indices, val_indices = indices[:train_size], indices[train_size:]
train_dataset = Subset(train_full, train_indices)
val_dataset = Subset(eval_full, val_indices)

train_labels = [train_full.samples[i][1] for i in train_indices]
class_counts = torch.bincount(torch.tensor(train_labels), minlength=NUM_CLASSES).float()
if (class_counts == 0).any():
    raise ValueError(f"At least one class has no training samples: {class_counts.tolist()}")
class_weights = (len(train_labels) / (NUM_CLASSES * class_counts)).to(DEVICE)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

print("=" * 68)
print("FER-2013 - RESNET18 LAYER3 + LAYER4 FINE-TUNING")
print("=" * 68)
print(f"Dataset: {DATASET_DIR}")
print(f"Images: {dataset_size} | Train: {train_size} | Validation: {val_size}")
print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE} | Batch: {BATCH_SIZE} | Epochs: {EPOCHS}")
print(f"Device: {DEVICE}")
print(f"Class counts: {dict(zip(EMOTION_CLASSES, class_counts.int().tolist()))}")
print(f"Checkpoint output: {MODEL_PATH}")
print("=" * 68)

print("\nLoading ImageNet-pretrained ResNet18...")
model = resnet18(weights=ResNet18_Weights.DEFAULT)
for parameter in model.parameters():
    parameter.requires_grad = False
for parameter in model.layer3.parameters():
    parameter.requires_grad = True
for parameter in model.layer4.parameters():
    parameter.requires_grad = True
model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=LABEL_SMOOTHING)
optimizer = torch.optim.AdamW([
    {"params": model.layer3.parameters(), "lr": LAYER3_LR},
    {"params": model.layer4.parameters(), "lr": LAYER4_LR},
    {"params": model.fc.parameters(), "lr": CLASSIFIER_LR},
], weight_decay=WEIGHT_DECAY)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)

print("Trainable layers: layer3, layer4, and final classifier.")
print("Existing baseline checkpoint will not be overwritten.")

def train_one_epoch():
    model.train()
    running_loss = correct = total = 0
    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad(set_to_none=True)
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)
    return running_loss / max(total, 1), correct / max(total, 1)

def validate():
    model.eval()
    running_loss = 0.0
    all_predictions, all_labels = [], []
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            running_loss += criterion(outputs, labels).item() * images.size(0)
            all_predictions.extend(outputs.argmax(dim=1).cpu().tolist())
            all_labels.extend(labels.cpu().tolist())
    total = max(len(all_labels), 1)
    val_loss = running_loss / total
    accuracy = sum(p == y for p, y in zip(all_predictions, all_labels)) / total
    macro_f1 = f1_score(all_labels, all_predictions, labels=list(range(NUM_CLASSES)), average="macro", zero_division=0)
    return val_loss, accuracy, macro_f1, all_labels, all_predictions

best_val_macro_f1 = -1.0
best_epoch = 0
best_val_labels, best_val_predictions = [], []
print("\nStarting training...")
for epoch in range(1, EPOCHS + 1):
    train_loss, train_accuracy = train_one_epoch()
    val_loss, val_accuracy, val_macro_f1, val_labels, val_predictions = validate()
    scheduler.step(val_macro_f1)
    lrs = "/".join(f"{group['lr']:.7f}" for group in optimizer.param_groups)
    print(
        f"Epoch [{epoch:02d}/{EPOCHS}] | train loss {train_loss:.4f} "
        f"| train acc {train_accuracy * 100:.2f}% | val loss {val_loss:.4f} "
        f"| val acc {val_accuracy * 100:.2f}% | val macro-F1 {val_macro_f1:.4f} | LRs {lrs}"
    )
    if val_macro_f1 > best_val_macro_f1:
        best_val_macro_f1 = val_macro_f1
        best_epoch = epoch
        best_val_labels, best_val_predictions = list(val_labels), list(val_predictions)
        torch.save({
            "model_state_dict": copy.deepcopy(model.state_dict()),
            "classes": EMOTION_CLASSES,
            "image_size": IMAGE_SIZE,
            "best_val_accuracy": val_accuracy,
            "best_val_macro_f1": val_macro_f1,
            "best_epoch": epoch,
            "model_name": "ResNet18-Layer3-Layer4-FineTuned",
        }, MODEL_PATH)
        print(f"  Saved new best checkpoint (validation macro-F1 {val_macro_f1:.4f})")

print("\n" + "=" * 68)
print("TRAINING COMPLETE")
print("=" * 68)
print(f"Best epoch: {best_epoch}")
print(f"Best validation macro-F1: {best_val_macro_f1:.4f}")
print(f"Saved checkpoint: {MODEL_PATH}")
print("\nBest-checkpoint epoch validation classification report:")
print(classification_report(
    best_val_labels, best_val_predictions, labels=list(range(NUM_CLASSES)),
    target_names=EMOTION_CLASSES, digits=4, zero_division=0,
))
print("These are validation results, not official test-set results.")
