import os
import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_caching import Cache
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv
import logging
import requests
import sqlite3
import pickle
from prompts.roles import system, user
from langchain.memory import ConversationBufferMemory  # Import LangChain memory
from vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://jolly-sky-0071d7d03.5.azurestaticapps.net",
                                         "http://localhost:3000"]}})

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

api_key = os.getenv('MIXTRAL_API_KEY')
if not api_key:
    raise ValueError("MIXTRAL_API_KEY environment variable is not set")

mistral_client = MistralClient(api_key=api_key)
mistral_model = "mistral-large-latest"

class MixtralAPIError(Exception):
    pass

@app.errorhandler(MixtralAPIError)
def handle_mixtral_api_error(error):
    return jsonify({'error': str(error)}), 500

# Initialize ConversationBufferMemory
memory = ConversationBufferMemory()

# Initialize vector store
vector_store = VectorStore()


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    n_results = 10  # Default number of results to retrieve
    
    if not user_message or not session_id:
        return jsonify({'error': 'Message and session_id are required'}), 400

    try:
        # Add user message to memory
        memory.chat_memory.add_user_message(user_message)

        # Fetch query results from vector store
        search_results_text = vector_store.query_embeddings(user_message, n_results=n_results)
        logging.info(f"Search results: {search_results_text}")  
        

        # Create the user prompt
        user_prompt = user.format(user_message=user_message,
                                  conv_history=memory.load_memory_variables({})['history'],
                                  n_results=n_results,
                                  search_results_text=search_results_text)
        
        logging.info(f"User prompt: {user_prompt}")

        messages = [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user_prompt}
        ]

        chat_response = mistral_client.chat(
            model=mistral_model,
            messages=messages
        )
        refined_response = chat_response.choices[0].message.content

        # Add AI response to memory
        memory.chat_memory.add_ai_message(refined_response)

        logging.info(f"Conversation history: {memory.load_memory_variables({})}")

    except Exception as e:
        logging.error(f"Failed to get response from Mistral API: {str(e)}")
        raise MixtralAPIError(f"Failed to get response from Mistral API: {str(e)}") from e

    return jsonify({'response': refined_response})

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    data = request.json
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    # Clear the conversation history for the session
    memory.chat_memory.clear()

    logging.info(f"Conversation history cleared for session: {session_id}")
    return jsonify({'message': 'Conversation history cleared'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
