import random
from pathlib import Path

import pandas as pd


# ============================================================
# Configuration
# ============================================================

SEED = 42
TARGET_SAMPLES = 15000

random.seed(SEED)

OUTPUT_PATH = (
    Path(__file__).resolve().parent
    / "dataset"
    / "synthetic_nlp_dataset.csv"
)


# ============================================================
# Student-life events
# ============================================================

EVENTS = [
    "I attended my morning classes",
    "I worked on my project",
    "I studied for an upcoming exam",
    "I finished one of my assignments",
    "I spent some time in the library",
    "I had a few lectures today",
    "I worked on some coding",
    "I stayed in my room after college",
    "I met a few classmates",
    "I had some college work to finish",
    "I spent the evening studying",
    "I worked on a presentation",
    "I revised some topics",
    "I went through my project work",
    "I had a regular college schedule",
]


# ============================================================
# Lower-concern experiences
# ============================================================

LOWER_EXPERIENCES = [
    "things felt manageable",
    "I was able to take things at my own pace",
    "I had enough energy to get through the day",
    "I could focus without too much trouble",
    "I felt comfortable with my routine",
    "I had enough time to relax",
    "I was satisfied with how the day went",
    "I felt reasonably positive",
    "I managed my work without rushing",
    "I was able to get things done",
    "my workload did not feel too difficult",
    "I felt like I was keeping up",
    "I had a decent amount of energy",
    "I was able to concentrate",
    "I felt fairly calm",
]


# ============================================================
# Elevated-concern experiences
# ============================================================

ELEVATED_EXPERIENCES = [
    "things have been harder to manage",
    "I have been struggling to keep up",
    "I have not had much energy lately",
    "it has been difficult to concentrate",
    "my routine has been difficult to maintain",
    "I have barely had time to switch off",
    "I have been finding normal tasks tiring",
    "I have been thinking about college work constantly",
    "I keep falling behind on things",
    "I have trouble getting started on tasks",
    "I have been finding it difficult to stay focused",
    "my usual routine feels harder than it should",
    "I have not been able to relax properly",
    "I feel like everything is taking more effort",
    "I have been having difficulty keeping my thoughts organized",
]


# ============================================================
# Lower-concern reflections
# ============================================================

LOWER_REFLECTIONS = [
    "I think I handled the day reasonably well",
    "I am looking forward to tomorrow",
    "I feel okay about what I need to do next",
    "I think I can manage the remaining work",
    "I am glad I got some time for myself",
    "I feel comfortable with how things are going",
    "I am trying to maintain a balanced routine",
    "I feel prepared for the next few days",
    "I was happy with the progress I made",
    "I think a good night's sleep will help",
]


# ============================================================
# Elevated-concern reflections
# ============================================================

ELEVATED_REFLECTIONS = [
    "I am not sure how to catch up",
    "I keep worrying about what I have left to do",
    "I wish I could get away from everything for a while",
    "I am finding it difficult to get back into my routine",
    "I feel like I need more time to recover",
    "I am not sure how long I can keep this pace",
    "I keep thinking about things even when I am trying to rest",
    "I hope I can get things under control soon",
    "I feel stuck with everything I need to handle",
    "I just want my mind to slow down",
]


# ============================================================
# Neutral / ambiguous experiences
# ============================================================

NEUTRAL_EXPERIENCES = [
    "The day was mostly about college work",
    "I spent several hours on my usual tasks",
    "I had a fairly busy schedule",
    "I did not do anything particularly different today",
    "Most of my time went into studying",
    "I followed my usual routine",
    "I had a lot of small things to finish",
    "The day passed mostly between classes and assignments",
    "I was busy for most of the afternoon",
    "I spent some time working and some time resting",
]


# ============================================================
# Coping / positive activities
# ============================================================

COPING_ACTIVITIES = [
    "I went for a short walk",
    "I listened to music for a while",
    "I talked to a friend",
    "I spent some time with my family",
    "I took a proper break",
    "I got some fresh air",
    "I watched something for a little while",
    "I took some time away from my laptop",
    "I had a quiet evening",
    "I tried to get some extra rest",
]


# ============================================================
# Casual student language
# ============================================================

CASUAL_PREFIXES = [
    "Honestly,",
    "To be honest,",
    "Lately,",
    "These days,",
    "Right now,",
    "At the moment,",
    "For some reason,",
    "I guess",
    "I think",
    "Somehow,",
    "",
    "",
    "",
]


CASUAL_SUFFIXES = [
    "Anyway, I will deal with it tomorrow.",
    "Hopefully things feel easier tomorrow.",
    "I am just taking it one day at a time.",
    "I think I need to slow down a little.",
    "That was pretty much my day.",
    "Nothing else really happened.",
    "I will try again tomorrow.",
    "I am hoping the next few days are better.",
    "",
    "",
    "",
]


# ============================================================
# Sentence construction
# ============================================================

def maybe_add_prefix(text):
    prefix = random.choice(CASUAL_PREFIXES)

    if not prefix:
        return text

    # Avoid awkward grammar such as "I guess I..."
    if prefix == "I guess":
        return f"{prefix} {text[0].lower()}{text[1:]}"

    return f"{prefix} {text}"


def maybe_add_suffix(text):
    suffix = random.choice(CASUAL_SUFFIXES)

    if suffix:
        return f"{text} {suffix}"

    return text


def create_lower_sample():
    event = random.choice(EVENTS)
    experience = random.choice(LOWER_EXPERIENCES)
    reflection = random.choice(LOWER_REFLECTIONS)
    neutral = random.choice(NEUTRAL_EXPERIENCES)
    coping = random.choice(COPING_ACTIVITIES)

    style = random.randint(1, 7)

    if style == 1:
        text = f"{event}. {experience}."

    elif style == 2:
        text = f"{experience}. {reflection}."

    elif style == 3:
        text = f"{event}. {experience}. {reflection}."

    elif style == 4:
        text = f"{neutral}. {experience}."

    elif style == 5:
        text = f"{event}. {coping}. {reflection}."

    elif style == 6:
        text = f"{experience}. {event}. {coping}."

    else:
        text = f"{neutral}. {experience}. {reflection}. {coping}."

    if random.random() < 0.25:
        text = maybe_add_prefix(text)

    if random.random() < 0.20:
        text = maybe_add_suffix(text)

    return text.strip()


def create_elevated_sample():
    event = random.choice(EVENTS)
    experience = random.choice(ELEVATED_EXPERIENCES)
    reflection = random.choice(ELEVATED_REFLECTIONS)
    neutral = random.choice(NEUTRAL_EXPERIENCES)
    coping = random.choice(COPING_ACTIVITIES)

    style = random.randint(1, 7)

    if style == 1:
        text = f"{event}. {experience}."

    elif style == 2:
        text = f"{experience}. {reflection}."

    elif style == 3:
        text = f"{event}. {experience}. {reflection}."

    elif style == 4:
        text = f"{neutral}. {experience}."

    elif style == 5:
        text = f"{event}. {experience}. {coping}."

    elif style == 6:
        text = f"{experience}. {event}. {coping}."

    else:
        text = f"{neutral}. {experience}. {reflection}. {coping}."

    if random.random() < 0.25:
        text = maybe_add_prefix(text)

    if random.random() < 0.20:
        text = maybe_add_suffix(text)

    return text.strip()


# ============================================================
# Generate candidate samples
# ============================================================

def generate_candidates(target_per_class):
    rows = []

    # Generate considerably more candidates than required.
    # This gives us room to remove duplicates.
    attempts = target_per_class * 4

    for _ in range(attempts):

        rows.append({
            "text": create_lower_sample(),
            "label": 0
        })

        rows.append({
            "text": create_elevated_sample(),
            "label": 1
        })

    return pd.DataFrame(rows)


# ============================================================
# Remove exact duplicates
# ============================================================

def clean_and_balance(df, target_per_class):

    # Remove exact duplicate text.
    df = df.drop_duplicates(
        subset=["text"]
    ).reset_index(drop=True)

    # Keep classes balanced.
    class_zero = df[df["label"] == 0]
    class_one = df[df["label"] == 1]

    available = min(
        len(class_zero),
        len(class_one),
        target_per_class
    )

    class_zero = class_zero.sample(
        n=available,
        random_state=SEED
    )

    class_one = class_one.sample(
        n=available,
        random_state=SEED
    )

    final_df = pd.concat(
        [class_zero, class_one],
        ignore_index=True
    )

    final_df = final_df.sample(
        frac=1,
        random_state=SEED
    ).reset_index(drop=True)

    return final_df


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    target_per_class = TARGET_SAMPLES // 2

    print("Generating candidate NLP samples...")

    candidates = generate_candidates(
        target_per_class
    )

    print(f"Candidate samples: {len(candidates)}")

    df = clean_and_balance(
        candidates,
        target_per_class
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nNLP dataset generated successfully.")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nFinal shape:")
    print(df.shape)

    print("\nLabel distribution:")
    print(df["label"].value_counts())

    print("\nUnique texts:")
    print(df["text"].nunique())

    print("\nDuplicates:")
    print(df["text"].duplicated().sum())

    print("\nDuplicate rate:")
    print(
        round(
            df["text"].duplicated().mean() * 100,
            2
        ),
        "%"
    )

    print("\nSample data:")
    print(
        df.sample(
            10,
            random_state=42
        ).to_string(index=False)
    )