from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
import os

from evaluator import evaluate_answer

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")


def load_questions(subject):
    """
    Load questions JSON based on subject name
    """
    file_path = os.path.join(QUESTIONS_DIR, f"{subject}.json")

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/get-question", methods=["GET"])
def get_question():
    subject = request.args.get("subject", "python")
    questions = load_questions(subject)

    if not questions:
        return jsonify({"error": "Subject not found"}), 404

    q = random.choice(questions)

    # IMPORTANT: Do NOT send answer to frontend
    return jsonify({
        "id": q["id"],
        "question": q["question"],
        "subject": subject
    })


@app.route("/submit-answer", methods=["POST"])
def submit_answer():
    data = request.json

    subject = data.get("subject")
    question_id = data.get("question_id")
    user_answer = data.get("user_answer")

    questions = load_questions(subject)

    if not questions:
        return jsonify({"error": "Invalid subject"}), 400

    question = next((q for q in questions if q["id"] == question_id), None)

    if not question:
        return jsonify({"error": "Question not found"}), 404

    score, feedback = evaluate_answer(user_answer, question["answer"])

    return jsonify({
        "score": score,
        "feedback": feedback
    })


if __name__ == "__main__":
    app.run(debug=True)