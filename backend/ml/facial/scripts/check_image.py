from pathlib import Path
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent
DATASET_DIR = ML_DIR / "dataset" / "fer2013"

IMAGE_PATH = (
    DATASET_DIR
    / "train"
    / "happy"
)


def main():
    images = list(IMAGE_PATH.iterdir())

    if not images:
        print("No images found.")
        return

    image_path = images[0]

    with Image.open(image_path) as image:
        print("FER-2013 Image Inspection")
        print("=" * 40)
        print(f"File       : {image_path.name}")
        print(f"Format     : {image.format}")
        print(f"Mode       : {image.mode}")
        print(f"Size       : {image.size}")
        print(f"Width      : {image.width}")
        print(f"Height     : {image.height}")


if __name__ == "__main__":
    main()