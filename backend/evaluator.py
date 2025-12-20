# evaluator.py
# This file contains ONLY evaluation logic (no Flask)

def normalize(text):
    return text.lower().strip()


def evaluate_answer(user_answer, correct_answer):
    """
    Evaluates the user's answer against the correct answer
    Returns: score (0–1), feedback string
    """

    user = normalize(user_answer)
    correct = normalize(correct_answer)

    if user == correct:
        return 1, "✅ Perfect answer"

    if user in correct or correct in user:
        return 0.5, "🟡 Partially correct answer"

    return 0, "❌ Incorrect answer"