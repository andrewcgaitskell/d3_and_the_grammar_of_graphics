from quart import Quart, jsonify, send_file
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

if __name__ == '__main__':
    app.run(debug=True)
