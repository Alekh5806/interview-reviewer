from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import random

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")

print("QUESTIONS DIR:", QUESTIONS_DIR)

@app.route("/api/question-set", methods=["GET"])
def get_question_set():
    subject = request.args.get("subject")

    if not subject:
        return jsonify({"error": "Subject missing"}), 400

    file_path = os.path.join(QUESTIONS_DIR, f"{subject}.json")
    print("LOADING:", file_path)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Failed to load questions"}), 500


if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)