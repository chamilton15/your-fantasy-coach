import asyncio
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import requests
import logging
from agents import Agent, FileSearchTool, Runner, trace
import os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

api_key = os.getenv("OPENAI_API_KEY")
# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Define the agent with FileSearchTool
agent = Agent(
    name="File searcher",
    instructions="All of your data that you are trained on is NFL data and NFL fantasy football data. You are a fantasy football expert and you are here to help the user with their fantasy football team.",
    tools=[
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["vs_67e31320aca481918168da9c07d462db"],
            include_search_results=True,
        )
    ],
)

async def ask_agent(input_text):
    """Runs the agent with a user query."""
    with trace("File search example"):
        result = await Runner.run(agent, input_text)
        # Convert the response to a string if it's not already
        final_output = str(result.final_output) if result.final_output else ""
        new_items = [str(item) for item in result.new_items] if result.new_items else []
        return final_output, new_items

@app.route("/ask", methods=["POST"])
def ask():
    input_text = request.json.get("text")
    if not input_text:
        return jsonify({"error": "No input provided"}), 400
    
    try:
        # Run the agent asynchronously and get response
        final_output, search_results = asyncio.run(ask_agent(input_text))

        # Log results
        logging.debug(f"User Input: {input_text}")
        logging.debug(f"Agent Response: {final_output}")
        logging.debug(f"Search Results: {search_results}")

        return jsonify({
            "answer": final_output,
            "search_results": search_results
        })
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return "Backend is running!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)


# @app.route('/n8nask', methods=['POST'])
# def n8nask():
#     input_text = request.json.get("text")
#     if not input_text:
#         return jsonify({"error": "No input provided"}), 400
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": input_text}],
#             max_tokens=150
#         )
#         answer = response.choices[0].message.content.strip()

#         # Log data being sent to n8n
#         logging.debug(f"Sending data to n8n: {input_text} -> {answer}")

#         # Send data to n8n webhook
#         webhook_url = "http://localhost:5678/webhook/fantasy_data"
#         payload = {"chatInput": f'Use the Wikipedia tool to retrieve additional information before responding: {input_text}', "answer": f'{answer}'}
#         response = requests.post(webhook_url, json=payload)

#         # Log response from n8n
#         logging.debug(f"n8n Response: {response.status_code} - {response.text}")

#         return jsonify({"answer": answer})
#     except Exception as e:
#         logging.error(f"Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500