import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests

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


@app.route("/")
def home():
    return jsonify({
        "status": "EduLearn Backend Running"
    })


@app.route("/courses")
def courses():
    return jsonify([
        {"id": 1, "name": "Python"},
        {"id": 2, "name": "Web Development"},
        {"id": 3, "name": "AI Fundamentals"}
    ])


@app.route("/chat", methods=["POST"])
def chat():

    try:

        if not OPENROUTER_API_KEY:
            return jsonify({
                "success": False,
                "reply": None,
                "error": "OPENROUTER_API_KEY not found on Render"
            }), 500

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "reply": None,
                "error": "No JSON received"
            }), 400

        user_message = data.get("message", "")

        print("User Message:", user_message)

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://edu-learn-weld.vercel.app",
                "X-Title": "EduLearn"
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
            },
            timeout=60
        )

        print("OpenRouter Status:", response.status_code)

        result = response.json()

        print("========== OPENROUTER RESPONSE ==========")
        print(result)
        print("========================================")

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "reply": None,
                "error": result
            }), response.status_code

        if "choices" not in result:
            return jsonify({
                "success": False,
                "reply": None,
                "error": "No choices returned by OpenRouter",
                "raw_response": result
            }), 500

        answer = result["choices"][0]["message"]["content"]

        return jsonify({
            "success": True,
            "reply": answer,
            "error": None
        })

    except Exception as e:

        print("SERVER ERROR:", str(e))

        return jsonify({
            "success": False,
            "reply": None,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )