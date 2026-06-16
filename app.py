import os
import sqlite3

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_db_connection():
    conn = sqlite3.connect("elearning.db")
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route("/register", methods=["POST"])
def register():

    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        existing_user = cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            conn.close()

            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 400

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users(name, email, password) VALUES(?,?,?)",
            (name, email, hashed_password)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Registration successful"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    

    
@app.route("/login", methods=["POST"])
def login():

    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        if not check_password_hash(user["password"], password):
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/chat", methods=["POST"])
def chat():

    try:

        print("API Key Exists:", bool(OPENROUTER_API_KEY))

        if not OPENROUTER_API_KEY:
            return jsonify({
                "success": False,
                "reply": None,
                "error": "OPENROUTER_API_KEY not found"
            }), 500

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "reply": None,
                "error": "No JSON received"
            }), 400

        user_message = data.get("message", "")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
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

        print("Status Code:", response.status_code)
        print("Raw Response:", response.text)

        result = response.json()

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "reply": None,
                "error": result
            }), response.status_code

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