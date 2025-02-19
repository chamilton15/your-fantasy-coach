from flask import Flask, request, jsonify
# import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# openai.api_key = ''

@app.route('/ask', methods=['POST'])
def ask():
    input = request.json.get("text")
    if not input:
        return jsonify({"error": "No input provided"}), 400
    return input
    
    # try:
    #     response = openai.Completion.create(
    #         engine="text-davinci-003",
    #         prompt=user_input,
    #         max_tokens=150
    #     )
    #     answer = response.choices[0].text.strip()
    #     return jsonify({"answer": answer})
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
