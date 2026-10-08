from pathlib import Path
from PIL import Image
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent
DATASET_DIR = ML_DIR / "dataset" / "fer2013"

IMAGE_DIR = DATASET_DIR / "train" / "happy"


def main():
    images = [
        file
        for file in IMAGE_DIR.iterdir()
        if file.is_file()
    ]

    if not images:
        print("No images found.")
        return

    image_path = images[0]

    with Image.open(image_path) as image:
        image_array = np.array(image)

    print("FER-2013 Pixel Inspection")
    print("=" * 40)
    print(f"Image       : {image_path.name}")
    print(f"Shape       : {image_array.shape}")
    print(f"Data type   : {image_array.dtype}")
    print(f"Minimum     : {image_array.min()}")
    print(f"Maximum     : {image_array.max()}")
    print(f"Mean        : {image_array.mean():.2f}")
    print(f"Unique pixels: {len(np.unique(image_array))}")


if __name__ == "__main__":
    main()