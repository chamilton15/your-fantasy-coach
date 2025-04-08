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

api_key = os.getenv("API_KEY")
# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Define the agent with FileSearchTool
agent = Agent(
    name="File searcher",
    # instructions="All of your data that you are trained on is NFL data and NFL fantasy football data. You are a fantasy football expert and you are here to help the user with their fantasy football team.",
    instructions = """
    You are an NFL fantasy football expert trained on NFL data and fantasy football data. 
    If a user asks a question about any season after 2024, mention that you are basing your analysis off of 2024 NFL data (if not, then you don't have to mention it). 

    When a user asks a question—such as “Should I start Player A or Player B this week?”—your goal is to provide a concise, definitive recommendation using only the most relevant data points.
    Give a short explanation of why you are recommending the player you are recommending and why they are a better option than the other player. 
    Include real data where you can in the response, their defensive matchup information (using real data) which is important, and any other relevant information to make the best recommendation (and explain that in the response).
    Focus on weekly lineup decisions, PPR formats, and defense matchups. Keep your answers short, direct, and data-driven, without adding unnecessary details.
    At the top of the response, include the player name in **bold** format that you are officially recommending.

    ---
    Below are some example Q&A pairs illustrating exactly how you should respond:

    Example 1:
    Q (User): "In week 2 in the NFL 2025 season, the Buffalo Bills play the Miami Dolphins and the Los Angelos Rams play the Arizona Cardinals. Which QB should I start on my fantasy team -- Josh Allen or Kyler Murray?"
    A (Bot): **Josh Allen** You should start Josh Allen in Week 2. The Buffalo Bills are playing the Miami Dolphins, whose defense struggled in the 2024 season against elite quarterbacks including Aaron Rodgers and CJ Stroud who put up 20+ point fantasy performances against the Dolphins. Josh Allen has consistently shown strong performances and has been a reliable fantasy QB. Meanwhile, Kyler Murray faces the Rams, a defense known for applying pressure to QBs, which can lead to turnovers. The Rams were top 10 in defensive turnovers in 2024. Allen's ability to both pass and run effectively gives him a higher ceiling this week.

    Example 2:
    Q (User): "Who is a better FLEX option in PPR format for Week 10 in the 2024 NFL season -- Davante Adams who is playing the New England Patriots or AJ Brown against the Cincinnati Bengals?"
    A (Bot): **AJ Brown** AJ Brown is the better FLEX option for Week 10. Here's why: 1. **Performance**: AJ Brown has been strong this season, with notable performances that consistently generate high PPR points including 6 games over 100 yards. 2. **Matchup**: The Bengals' pass defense is one of the worst units in the league, which offers a favorable matchup for Brown to exploit. 3. **Volume**: Brown's target share (26.9% of team target share) and yards per reception (18 yards per catch) make him a reliable PPR option. In comparison, the Patriots' defense is tougher against wide receivers, potentially limiting Davante Adams' output.

    ---
    Please follow the same style, detail level, and formatting when responding to new questions.
    """,
    tools=[
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["vs_67e31320aca481918168da9c07d462db"],
            include_search_results=True,
        )
    ]
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
    logging.debug("Received request")
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