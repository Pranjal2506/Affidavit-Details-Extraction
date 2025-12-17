from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from functions import process_pdf

app = Flask(__name__)
CORS(app) 

@app.route("/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf = request.files["file"]
    # path = f"temp_{pdf.filename}"
    path = f"/tmp/{pdf.filename}"
    pdf.save(path)

    try:
        data = process_pdf(path)
        return jsonify(data)
    finally:
        os.remove(path)

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8000)