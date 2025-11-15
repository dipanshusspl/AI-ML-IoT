# analyze_data.py
import pandas as pd

def analyze_data(excel_file="students.xlsx"):
    df = pd.read_excel(excel_file)
    print("✅ Data loaded successfully!")
    print(df)

    mean_age = df["Age"].mean()
    median_marks = df["Marks"].median()
    mode_city = df["City"].mode()[0]

    print("\n📈 Basic Statistics:")
    print(f"Mean Age: {mean_age:.2f}")
    print(f"Median Marks: {median_marks}")
    print(f"Most Common City: {mode_city}")

    return df, mean_age, median_marks, mode_city

if __name__ == "__main__":
    analyze_data()
