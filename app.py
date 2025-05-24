from quart import Quart, jsonify, send_file, render_template
import os
import json

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

if __name__ == '__main__':
    app.run(debug=True)
