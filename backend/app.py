from flask import Flask, request, jsonify
from flask_cors import CORS
import openpyxl
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- DYNAMIC PATH CONFIGURATION ---
# Since app.py is in /Backend, BASE_DIR is project/Backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# 1. Excel is in the same folder as app.py (Backend/)
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "Users.xlsx")

# 2. Questions folder is in the root directory (outside Backend/)
QUESTIONS_DIR = os.path.join(PROJECT_ROOT, "questions")

# --- 🔐 FEATURE 1: EXCEL LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_enrollment = str(data.get('enrollment'))
    user_password = str(data.get('password'))

    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            return jsonify({"success": False, "message": f"Database not found at {EXCEL_FILE_PATH}"}), 500

        workbook = openpyxl.load_workbook(EXCEL_FILE_PATH)
        sheet = workbook.active
        is_authenticated = False

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[0] or not row[1]: continue
            
            sheet_enrollment = str(row[0])
            raw_dob = row[1]

            formatted_pass = ""
            if isinstance(raw_dob, datetime):
                formatted_pass = raw_dob.strftime("%d%m%Y")
            else:
                try:
                    # Handle text fallback if Excel cell isn't a Date object
                    date_obj = datetime.strptime(str(raw_dob).strip(), "%d/%m/%Y")
                    formatted_pass = date_obj.strftime("%d%m%Y")
                except: continue

            if sheet_enrollment == user_enrollment and formatted_pass == user_password:
                is_authenticated = True
                break

        if is_authenticated:
            return jsonify({"success": True, "message": "Login Successful"}), 200
        return jsonify({"success": False, "message": "Invalid Enrollment or DOB"}), 401

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"success": False, "message": "Server Error"}), 500

# --- 📚 FEATURE 2: QUESTION LOADER ---
@app.route("/api/question-set", methods=["GET"])
def get_question_set():
    subject = request.args.get("subject")
    if not subject:
        return jsonify({"error": "Subject missing"}), 400

    file_path = os.path.join(QUESTIONS_DIR, f"{subject}.json")
    
    if not os.path.exists(file_path):
        return jsonify({"error": f"Subject file '{subject}.json' not found at {file_path}"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Question Load Error: {e}")
        return jsonify({"error": "Failed to load questions"}), 500

# --- START SERVER ---
if __name__ == "__main__":
    print(f"--- Neural Server Starting ---")
    print(f"Excel Path: {EXCEL_FILE_PATH}")
    print(f"Questions Path: {QUESTIONS_DIR}")
    app.run(port=5000, debug=True)