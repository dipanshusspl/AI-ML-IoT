from flask import Flask, render_template
import json
import subprocess
import os

app = Flask(__name__)

# Load project list
with open("projects.json") as f:
    PROJECTS = json.load(f)

@app.route("/")
def index():
    return render_template("index.html", menus=PROJECTS)

@app.route("/run/<category>/<int:index>")
def run_project(category, index):
    project = PROJECTS[category][index]
    project_path = os.path.abspath(project["path"])

    # Run the python script
    subprocess.Popen(["python", project_path])

    return render_template("run_project.html", project=project, category=category)

if __name__ == "__main__":
    app.run(debug=True)
