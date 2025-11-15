# load_kaggle_data.py
import pandas as pd

def load_kaggle_dataset():
    df = pd.read_csv("StudentsPerformance.csv")
    print("✅ Data loaded successfully from Kaggle!")
    print(df.head())

    # Basic info
    print("\nData Summary:")
    print(df.info())
    print("\nStatistical Overview:")
    print(df.describe())

    # Example: calculate mean of math, reading, writing scores
    mean_math = df["math score"].mean()
    median_reading = df["reading score"].median()
    mode_gender = df["gender"].mode()[0]

    print("\n📈 Basic Stats:")
    print(f"Mean Math Score: {mean_math:.2f}")
    print(f"Median Reading Score: {median_reading}")
    print(f"Most Common Gender: {mode_gender}")

    return df, mean_math, median_reading, mode_gender

if __name__ == "__main__":
    load_kaggle_dataset()
