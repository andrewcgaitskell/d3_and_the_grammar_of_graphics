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
    
    file_path = os.path.join("data", "dmtools_e.json")
    with open(file_path, "r") as f:
        data = json.load(f)

    spec = {
        "aes": {"x": 0, "y": 1},  # use index or field names if data is dicts
        "scales": {"x": "log", "y": "log"},
        "geom": {
            "type": "line",
            "dataKey": "data",
            "strokeWidth": 2
        },
        "labels": {
            "title": "WIMP Cross Section vs Mass",
            "x": "WIMP Mass [GeV/c²]",
            "y": "Cross Section [cm²] (normalized to nucleon)"
        },
        "colorScheme": "schemeCategory10",
        "margin": { "top": 60, "right": 30, "bottom": 60, "left": 80 },
        "width": 600,
        "height": 600
    }

    return await render_template("d3_dmtools_grammar.html", data=data, spec=spec)

if __name__ == '__main__':
    app.run(debug=True)
