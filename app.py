@app.route("/chat", methods=["POST"])
def chat():

    try:

        # Debug API key
        print("API Key Exists:", bool(OPENROUTER_API_KEY))

        if OPENROUTER_API_KEY:
            print("API Key Prefix:", OPENROUTER_API_KEY[:15])

        if not OPENROUTER_API_KEY:
            return jsonify({
                "success": False,
                "reply": None,
                "error": "OPENROUTER_API_KEY not found"
            }), 500

        data = request.get_json()

        user_message = data.get("message", "")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
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
            "reply": answer
        })

    except Exception as e:

        print("SERVER ERROR:", str(e))

        return jsonify({
            "success": False,
            "reply": None,
            "error": str(e)
        }), 500