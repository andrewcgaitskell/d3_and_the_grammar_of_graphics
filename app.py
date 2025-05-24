from quart import Quart, jsonify, send_file, render_template
import os
import json

from datetime import datetime, timedelta


app = Quart(__name__)

@app.route('/')
async def index():
    return "DMTools API is running."

@app.route('/api/dmtools')
async def get_dmtools_data():
    file_path = os.path.join("data", "dmtools.json")
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    with open(file_path, "r") as f:
        data = json.load(f)

    return jsonify(data)

@app.route('/chart')
async def chart():
    file_path = os.path.join("data", "dmtools.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return await render_template("dmtools.html", dmtools=data)

@app.route('/d3_dmtools')
async def d3_dmtools():
    file_path = os.path.join("data", "dmtools.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return await render_template("d3_dmtools.html", data=data)

@app.route('/d3_dmtools_e')
async def d3_dmtools_e():
    file_path = os.path.join("data", "dmtools_e.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return await render_template("d3_dmtools_e.html", data=data)

@app.route("/d3_dmtools_grammar")
async def d3_dmtools_grammar():
    data_file_path = os.path.join("data", "dmtools_e.json")
    spec_file_path = os.path.join("data", "chart_spec_grammar.json")
    display_file_path = os.path.join("data", "dmtools_displays_spec.json")
    
    with open(data_file_path) as f:
        data = json.load(f)
        
    with open(spec_file_path) as s:
        chart_spec = json.load(s)

    with open(display_file_path) as d:
        display_spec = json.load(d)

    return await render_template("d3_dmtools_grammar.html", data=data, chart_spec=chart_spec, display_spec=display_spec)

@app.route("/gantt")
async def gantt_chart():
    # Example task data
    tasks = [
        {"name": "Task A", "start": "2025-05-01", "end": "2025-05-05"},
        {"name": "Task B", "start": "2025-05-03", "end": "2025-05-10"},
        {"name": "Task C", "start": "2025-05-06", "end": "2025-05-09"}
    ]
    return await render_template("d3_gantt.html", tasks=tasks)

@app.route("/sequenced")
async def sequenced():
    # Step 1: Raw input task data
    raw_tasks = [
        {"id": "1", "name": "Task A", "start": "2025-05-01", "duration": 4},
        {"id": "2", "name": "Task B", "duration": 5, "depends_on": "1"},
        {"id": "3", "name": "Milestone C", "duration": 0, "depends_on": "2", "milestone": True},
        {"id": "4", "name": "Task D", "duration": 3, "depends_on": "2"},
    ]

    print("Raw Tasks Input:")
    for t in raw_tasks:
        print(t)

    # Step 2: Build full task list with sequencing
    task_map = {}
    processed_tasks = []

    for task in raw_tasks:
        # Determine start date
        if "depends_on" in task:
            predecessor = task_map[task["depends_on"]]
            start_date = datetime.strptime(predecessor["end"], "%Y-%m-%d") + timedelta(days=1)
        else:
            start_date = datetime.strptime(task["start"], "%Y-%m-%d")

        # Determine end date based on duration
        duration = task.get("duration", 0)
        end_date = start_date + timedelta(days=max(duration - 1, 0))

        # Format dates
        task["start"] = start_date.strftime("%Y-%m-%d")
        task["end"] = end_date.strftime("%Y-%m-%d")

        # Save to maps
        task_map[task["id"]] = task
        processed_tasks.append(task)

        print(f"Processed Task {task['id']}: start={task['start']}, end={task['end']}")

    print("Final Sequenced Task List:")
    for t in processed_tasks:
        print(t)

    # Step 3: Render
    return await render_template("d3_sequenced.html", tasks=processed_tasks)

if __name__ == '__main__':
    app.run(debug=True)
