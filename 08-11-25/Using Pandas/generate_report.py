# generate_report.py
from analyze_data import analyze_data
from pathlib import Path

def generate_html_report():
    df, mean_age, median_marks, mode_city = analyze_data()

    html = f"""
    <html>
    <head>
        <title>Student Report</title>
        <style>
            body {{
                font-family: Arial;
                background-color: #f8f9fa;
                margin: 40px;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                border-collapse: collapse;
                width: 80%;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #0078d7;
                color: white;
            }}
            .stats {{
                font-size: 18px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <h1>📊 Student Data Report</h1>
        {df.to_html(index=False)}
        <div class="stats">
            <p><b>Mean Age:</b> {mean_age:.2f}</p>
            <p><b>Median Marks:</b> {median_marks}</p>
            <p><b>Most Common City:</b> {mode_city}</p>
        </div>
    </body>
    </html>
    """

    path = Path("student_report.html")
    path.write_text(html, encoding="utf-8")
    print(f"✅ HTML report generated at: {path.resolve()}")

if __name__ == "__main__":
    generate_html_report()
