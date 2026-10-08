from pathlib import Path
from collections import Counter

import torch
from torchvision import datasets


SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent
DATASET_DIR = ML_DIR / "dataset" / "fer2013"

TRAIN_DIR = DATASET_DIR / "train"


def main():
    dataset = datasets.ImageFolder(TRAIN_DIR)

    counts = Counter(dataset.targets)

    print("FER-2013 Class Distribution")
    print("=" * 40)

    for class_index, class_name in enumerate(dataset.classes):
        print(
            f"{class_name:<10}: "
            f"{counts[class_index]} images"
        )

    total = len(dataset)
    num_classes = len(dataset.classes)

    weights = []

    for class_index in range(num_classes):
        weight = total / (
            num_classes * counts[class_index]
        )
        weights.append(weight)

    weights = torch.tensor(weights, dtype=torch.float32)

    print("\nClass Weights")
    print("=" * 40)

    for class_name, weight in zip(
        dataset.classes,
        weights
    ):
        print(
            f"{class_name:<10}: "
            f"{weight.item():.4f}"
        )


if __name__ == "__main__":
    main()