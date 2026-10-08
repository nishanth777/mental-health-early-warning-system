from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent.parent
DATASET_DIR = ML_DIR / "dataset" / "fer2013"

TRAIN_DIR = DATASET_DIR / "train"
TEST_DIR = DATASET_DIR / "test"

EMOTIONS = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
]


def count_images(folder):
    if not folder.exists():
        return 0

    return sum(
        1
        for file in folder.iterdir()
        if file.is_file()
    )


def inspect_split(split_name, split_dir):
    print(f"\n{split_name.upper()} DATASET")
    print("-" * 40)

    total = 0

    for emotion in EMOTIONS:
        emotion_dir = split_dir / emotion
        count = count_images(emotion_dir)

        print(f"{emotion:<10}: {count}")

        total += count

    print("-" * 40)
    print(f"{'TOTAL':<10}: {total}")

    return total


def main():
    print("FER-2013 Dataset Inspection")
    print("=" * 40)

    train_total = inspect_split("Train", TRAIN_DIR)
    test_total = inspect_split("Test", TEST_DIR)

    print("\nOVERALL")
    print("-" * 40)
    print(f"Training images : {train_total}")
    print(f"Testing images  : {test_total}")
    print(f"Total images    : {train_total + test_total}")


if __name__ == "__main__":
    main()