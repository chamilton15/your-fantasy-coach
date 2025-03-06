from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
# Initialize OpenAI client
client = openai.OpenAI(api_key='API_KEY')

@app.route('/ask', methods=['POST'])
def ask():
    input_text = request.json.get("text")
    if not input_text:
        return jsonify({"error": "No input provided"}), 400
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": input_text}],
            max_tokens=150
        )
        answer = response.choices[0].message.content.strip()

        # Log data being sent to n8n
        logging.debug(f"Sending data to n8n: {input_text} -> {answer}")

        # Send data to n8n webhook
        webhook_url = "http://localhost:5678/webhook/fantasy_data"
        payload = {"chatInput": input_text, "answer": answer}
        response = requests.post(webhook_url, json=payload)

        # Log response from n8n
        logging.debug(f"n8n Response: {response.status_code} - {response.text}")

        return jsonify({"answer": answer})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "Backend is running!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
