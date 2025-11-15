# create_df_to_excel.py
import pandas as pd
from pathlib import Path

# 1) Data as a dictionary
data = {
    "Name": ["Amit", "Riya", "John", "Sara", "Vikram"],
    "Age": [23, 25, 29, 22, 24],
    "Marks": [85, 90, 78, 88, 92],
    "City": ["Pune", "Delhi", "Mumbai", "Bangalore", "Chennai"]
}

# 2) Make a DataFrame
df = pd.DataFrame(data)

# 3) Optional: quick inspection (prints to console)
print("DataFrame preview:")
print(df.head())

# 4) Save to Excel (same folder)
output_path = Path("students.xlsx")
df.to_excel(output_path, index=False)   # index=False avoids writing the DataFrame index as a column

print(f"✅ Excel file written to: {output_path.resolve()}")
