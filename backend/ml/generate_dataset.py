import random
import pandas as pd

NUM_SAMPLES = 15000

data = []

def generate_healthy_student():
    return {
        "sleep_hours": round(random.uniform(7, 9), 1),
        "sleep_quality": random.randint(4, 5),
        "stress_level": random.randint(1, 2),
        "academic_pressure": random.randint(1, 3),
        "mood": random.randint(4, 5),
        "energy_level": random.randint(4, 5),
        "social_interaction": random.randint(4, 5),
        "exercise_minutes": random.randint(30, 90),
        "screen_time": round(random.uniform(2, 5), 1),
        "study_hours": round(random.uniform(2, 6), 1),
        "depression": 0 if random.random() < 0.95 else 1
    }
def generate_moderate_student():
    return {
        "sleep_hours": round(random.uniform(5.5, 7), 1),
        "sleep_quality": random.randint(2, 4),
        "stress_level": random.randint(2, 4),
        "academic_pressure": random.randint(2, 4),
        "mood": random.randint(2, 4),
        "energy_level": random.randint(2, 4),
        "social_interaction": random.randint(2, 4),
        "exercise_minutes": random.randint(10, 40),
        "screen_time": round(random.uniform(4, 8), 1),
        "study_hours": round(random.uniform(4, 8), 1),
        "depression": 1 if random.random() < 0.50 else 0
    }
def generate_high_risk_student():
    return {
        "sleep_hours": round(random.uniform(3, 5), 1),
        "sleep_quality": random.randint(1, 2),
        "stress_level": random.randint(4, 5),
        "academic_pressure": random.randint(4, 5),
        "mood": random.randint(1, 2),
        "energy_level": random.randint(1, 2),
        "social_interaction": random.randint(1, 2),
        "exercise_minutes": random.randint(0, 10),
        "screen_time": round(random.uniform(8, 12), 1),
        "study_hours": round(random.uniform(7, 12), 1),
        "depression": 1 if random.random() < 0.95 else 0
    }
def generate_student():
    profile = random.random()

    if profile < 0.45:
        return generate_healthy_student()

    elif profile < 0.75:
        return generate_moderate_student()

    else:
        return generate_high_risk_student()

def main():

    for _ in range(NUM_SAMPLES):
        data.append(generate_student())

    # Create DataFrame
    df = pd.DataFrame(data)

    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save dataset
    df.to_csv("dataset/synthetic_assessment_dataset.csv", index=False)

    print("✅ Dataset generated successfully!")

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nDataset Shape:")
    print(df.shape)

    print("\nDepression Distribution:")
    print(df["depression"].value_counts())

    print("\nDepression Percentage:")
    print((df["depression"].value_counts(normalize=True) * 100).round(2))


if __name__ == "__main__":
    main()