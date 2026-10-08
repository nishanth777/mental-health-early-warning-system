from pathlib import Path

import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent
DATASET_DIR = ML_DIR / "dataset" / "fer2013"

TRAIN_DIR = DATASET_DIR / "train"


transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
])


def main():
    dataset = datasets.ImageFolder(
        root=TRAIN_DIR,
        transform=transform
    )

    dataloader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True,
        num_workers=0
    )

    images, labels = next(iter(dataloader))

    print("FER-2013 DataLoader Test")
    print("=" * 40)
    print(f"Number of images : {len(dataset)}")
    print(f"Number of classes: {len(dataset.classes)}")
    print(f"Classes          : {dataset.classes}")
    print(f"Batch shape      : {images.shape}")
    print(f"Label shape      : {labels.shape}")
    print(f"Image dtype      : {images.dtype}")
    print(f"Image min        : {images.min():.4f}")
    print(f"Image max        : {images.max():.4f}")


if __name__ == "__main__":
    main()