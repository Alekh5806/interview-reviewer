from flask import Flask, request, jsonify
from flask_cors import CORS
import openpyxl
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Path to your Excel file inside the Backend folder
EXCEL_FILE_PATH = './Backend/Users.xlsx'

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_enrollment = str(data.get('enrollment'))
    user_password = str(data.get('password')) # Expected in ddmmyyyy format

    try:
        workbook = openpyxl.load_workbook(EXCEL_FILE_PATH)
        sheet = workbook.active
        
        is_authenticated = False

        # Iterate through rows, skipping the header (row 1)
        for row in sheet.iter_rows(min_row=2, values_only=True):
            sheet_enrollment = str(row[0]) # Column A: Enrollment
            raw_dob = row[1]               # Column B: Date of Birth

            # Convert Excel Date object to ddmmyyyy string
            formatted_pass = ""
            if isinstance(raw_dob, datetime):
                formatted_pass = raw_dob.strftime("%d%m%Y")
            else:
                # Fallback if Excel cell is stored as text (e.g., "10/03/2007")
                try:
                    # Clean the string and parse it
                    date_obj = datetime.strptime(str(raw_dob).strip(), "%d/%m/%Y")
                    formatted_pass = date_obj.strftime("%d%m%Y")
                except ValueError:
                    continue

            if sheet_enrollment == user_enrollment and formatted_pass == user_password:
                is_authenticated = True
                break

        if is_authenticated:
            return jsonify({"success": True, "message": "Login Successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid Enrollment or DOB"}), 401

    except Exception as e:
        print(f"Excel Read Error: {e}")
        return jsonify({"success": False, "message": "Server Error"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)