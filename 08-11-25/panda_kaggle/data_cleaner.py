
import pandas as pd
import matplotlib.pyplot as plt

# 1️⃣ Load dataset
file_path = "StudentsPerformance.csv"  # Update path if needed
print(f"📂 Loading dataset from: {file_path}")
df = pd.read_csv(file_path)

# 2️⃣ Basic info
print("\n=== BASIC DATA INFO ===")
print(df.info())
print("\nTop 5 Rows:")
print(df.head())

# 3️⃣ Check for missing values
print("\n=== MISSING VALUE REPORT ===")
missing_values = df.isnull().sum()
print(missing_values[missing_values > 0] if missing_values.sum() > 0 else "No missing values found ✅")

# Fill missing numeric values with column mean (if any)
numeric_cols = df.select_dtypes(include="number").columns
for col in numeric_cols:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].mean(), inplace=True)

# 4️⃣ Check for duplicate rows
print("\n=== DUPLICATE CHECK ===")
duplicates = df.duplicated().sum()
print(f"Duplicate rows found: {duplicates}")
if duplicates > 0:
    df.drop_duplicates(inplace=True)
    print("✅ Duplicates removed.")

# 5️⃣ Clean categorical text data (trim spaces, capitalize)
cat_cols = df.select_dtypes(include="object").columns
for col in cat_cols:
    df[col] = df[col].astype(str).str.strip().str.title()

# 6️⃣ Check numeric value validity (0–100 range for scores)
score_cols = [col for col in df.columns if "score" in col.lower()]
invalid_rows = pd.DataFrame()
for col in score_cols:
    invalid = df[(df[col] < 0) | (df[col] > 100)]
    if not invalid.empty:
        invalid_rows = pd.concat([invalid_rows, invalid])
        df = df[(df[col] >= 0) & (df[col] <= 100)]
if not invalid_rows.empty:
    print(f"\nRemoved {len(invalid_rows)} rows with invalid scores.")
else:
    print("\n✅ All score values are within 0–100.")

# 7️⃣ Compare before & after cleaning
print("\n=== CLEANING SUMMARY ===")
print(f"Total rows after cleaning: {len(df)}")

# 8️⃣ Basic Statistics
print("\n=== BASIC STATISTICS ===")
for col in score_cols:
    print(f"\n📘 {col}:")
    print(f"  Mean  : {df[col].mean():.2f}")
    print(f"  Median: {df[col].median():.2f}")
    print(f"  Mode  : {df[col].mode()[0]}")

# 9️⃣ Save cleaned dataset
cleaned_path = "Cleaned_StudentsPerformance.csv"
df.to_csv(cleaned_path, index=False)
print(f"\n✅ Cleaned data saved to: {cleaned_path}")

# 🔟 Optional: visualize score distributions
for col in score_cols:
    plt.figure()
    df[col].hist(bins=10)
    plt.title(f"{col} Distribution")
    plt.xlabel(col)
    plt.ylabel("Count")
    plt.show()
