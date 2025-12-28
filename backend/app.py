from flask import Flask, request, jsonify
from flask_cors import CORS
import openpyxl
import os
import json
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION (Paths for Backend/ folder) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "Users.xlsx")
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")

# --- 🔐 FEATURE 1: EXCEL LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_enrollment = str(data.get('enrollment', '')).strip()
    user_password = str(data.get('password', '')).strip()

    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            return jsonify({"success": False, "message": "Database file missing"}), 500

        workbook = openpyxl.load_workbook(EXCEL_FILE_PATH)
        sheet = workbook.active
        is_authenticated = False

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] is None or row[1] is None: continue
            
            sheet_enrollment = str(row[0]).strip()
            raw_dob = row[1]

            formatted_pass = ""
            if isinstance(raw_dob, datetime):
                formatted_pass = raw_dob.strftime("%d%m%Y")
            else:
                try:
                    date_obj = datetime.strptime(str(raw_dob).strip(), "%d/%m/%Y")
                    formatted_pass = date_obj.strftime("%d%m%Y")
                except: continue

            if sheet_enrollment == user_enrollment and formatted_pass == user_password:
                is_authenticated = True
                break

        if is_authenticated:
            return jsonify({"success": True, "message": "Login Successful"}), 200
        return jsonify({"success": False, "message": "Invalid Credentials"}), 401

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500

# --- 📚 FEATURE 2: QUESTION LOADER ---
@app.route("/api/question-set", methods=["GET"])
def get_question_set():
    subject = request.args.get("subject")
    if not subject:
        return jsonify({"error": "Subject missing"}), 400

    file_path = os.path.join(QUESTIONS_DIR, f"{subject}.json")
    if not os.path.exists(file_path):
        return jsonify({"error": f"Track '{subject}' not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Fetch Error: {e}")
        return jsonify({"error": "Failed to load questions"}), 500

if __name__ == "__main__":
    print(f"\n🚀 Neural Server Active at: http://127.0.0.1:5000")
    app.run(port=5000, debug=True)