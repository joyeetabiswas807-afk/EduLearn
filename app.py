import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print("API Key Loaded:", bool(OPENROUTER_API_KEY))

SYSTEM_PROMPT = """
You are EduLearn AI Tutor.

You help students learn:
- Python
- Web Development
- Artificial Intelligence
- Data Structures
- Computer Science

Rules:
- Explain concepts simply.
- Give examples.
- Generate notes if requested.
- Generate MCQs if requested.
- Generate study plans if requested.
- Be friendly and educational.
"""

# Home Route
@app.route("/")
def home():
    return jsonify({
        "status": "EduLearn Backend Running"
    })

# Courses Route
@app.route("/courses")
def courses():
    return jsonify([
        {"id": 1, "name": "Python"},
        {"id": 2, "name": "Web Development"},
        {"id": 3, "name": "AI Fundamentals"}
    ])

# AI Chat Route
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message", "")

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }
        )

        result = response.json()

        if "choices" not in result:
            return jsonify({
                "success": False,
                "error": result
            })

        answer = result["choices"][0]["message"]["content"]

        return jsonify({
            "success": True,
            "reply": answer
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

# Start Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
