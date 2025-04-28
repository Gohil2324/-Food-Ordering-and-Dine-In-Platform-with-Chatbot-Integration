import requests
from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

OLLAMA_URL = "http://localhost:11434/api/generate"  # adjust if remote

@chatbot_bp.route('/chatbot', methods=['POST'])
def chat_with_bot():
    user_input = request.json.get("message")

    payload = {
        "model": "mistral",  # Change to your model if different is AI
        "prompt": user_input, #message from user
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        reply = response.json()["response"]
        return jsonify({"reply": reply})
    else:
        return jsonify({"error": "Chatbot not responding"}), 500
