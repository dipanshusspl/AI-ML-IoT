# create_data.py
import pandas as pd

def create_dataframe():
    # More sample data — 20 students
    data = {
        "Name": [
            "Amit", "Riya", "John", "Sara", "Vikram",
            "Priya", "Arjun", "Sneha", "Rohit", "Nisha",
            "Karan", "Tina", "Deepak", "Meena", "Rahul",
            "Anita", "Mohit", "Pooja", "Ramesh", "Kavita"
        ],
        "Age": [
            23, 25, 29, 22, 24,
            26, 21, 27, 28, 23,
            24, 22, 29, 25, 21,
            30, 23, 24, 28, 27
        ],
        "Marks": [
            85, 90, 78, 88, 92,
            80, 83, 95, 76, 89,
            91, 84, 87, 93, 79,
            82, 96, 81, 77, 88
        ],
        "City": [
            "Pune", "Delhi", "Mumbai", "Bangalore", "Chennai",
            "Hyderabad", "Pune", "Delhi", "Kolkata", "Mumbai",
            "Chennai", "Hyderabad", "Bangalore", "Pune", "Delhi",
            "Kolkata", "Mumbai", "Chennai", "Pune", "Bangalore"
        ]
    }

    df = pd.DataFrame(data)
    print("✅ DataFrame created successfully with 20 rows:\n")
    print(df)
    print("\n🔢 Total rows:", len(df))
    return df

if __name__ == "__main__":
    create_dataframe()
