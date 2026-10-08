from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent
DATASET_DIR = ML_DIR / "dataset" / "fer2013"

TRAIN_DIR = DATASET_DIR / "train"

EMOTIONS = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
]


def main():
    print("FER-2013 Class Verification")
    print("=" * 40)

    for emotion in EMOTIONS:
        folder = TRAIN_DIR / emotion

        images = [
            file
            for file in folder.iterdir()
            if file.is_file()
        ]

        print(f"{emotion:<10}: {len(images)} images")

    print("=" * 40)
    print(f"Classes: {len(EMOTIONS)}")


if __name__ == "__main__":
    main()