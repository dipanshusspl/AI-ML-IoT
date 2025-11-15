# save_to_excel.py
from create_data import create_dataframe
from pathlib import Path

def save_to_excel():
    df = create_dataframe()
    path = Path("students.xlsx")
    df.to_excel(path, index=False)
    print(f"✅ Excel file saved at: {path.resolve()}")

if __name__ == "__main__":
    save_to_excel()
