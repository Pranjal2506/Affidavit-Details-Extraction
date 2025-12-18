from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from functions import process_pdf
import mysql.connector
import logging

app = Flask(__name__)
CORS(app) 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

def get_db():
    return mysql.connector.connect(
        host="db",
        user="root",
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=3306
    )

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            age INT,
            phone VARCHAR(20),
            pan VARCHAR(20),
            pan_confidence FLOAT,
            guardians_name VARCHAR(255),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        logger.info("Initializing DB...")
        db.commit()
    except Exception as e:
        logger.error("DB init failed", exc_info=True)
    cursor.close()
    db.close()

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
        # data = {"name": "Pranjal Raghuvanshi", "age": 25, "phone": 1234321231, "pan": "ABCDE1234F", "address": "123, Some Street, Some City, Some Country"}
        db = get_db()
        cursor = db.cursor()
        query = """
            INSERT INTO extracted_data (name, age, phone, pan, pan_confidence, guardians_name, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

        values = (
            data.get("name"),
            data.get("age"),
            str(data["phone"]) if data.get("phone") else None,
            data.get("pan"),
            float(data.get("pan_confidence", 0.0)),
            data.get("guardians_name"),
            data.get("address")
        )

        try:
            cursor.execute(query, values)
            db.commit()
            logger.info("Data inserted successfully")
        except Exception as e:
            logger.error("DB insert failed", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500
        cursor.close()
        db.close()
        return jsonify(data)
    finally:
        os.remove(path)
        
db_initialized = False
@app.before_request
def startup():
    global db_initialized
    if not db_initialized:
        init_db()
        db_initialized = True

    
if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8000)