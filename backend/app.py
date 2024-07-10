import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_caching import Cache
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv
import logging
import chromadb
import requests

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

# Initialize ChromaDB client
client = chromadb.Client()
dataset_collection = client.create_collection('dataset_names')

@app.route('/')
def home():
    return "Welcome to the Mixtral Chatbot!"

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello from Flask!'})

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        abort(400, description='Message is required')

    logging.info(f"Received message from frontend: {user_message}")

    try:
        chat_response = mistral_client.chat(
            model=mistral_model,
            messages=[ChatMessage(role="user", content=user_message)],
        )
        mixtral_response = chat_response.choices[0].message.content

        logging.info(f"Response from Mixtral: {mixtral_response}")
    except Exception as e:
        logging.error(f"Failed to get response from Mixtral API: {str(e)}")
        raise MixtralAPIError(f"Failed to get response from Mixtral API: {str(e)}") from e

    return jsonify({'response': mixtral_response})

@app.route('/initialize', methods=['POST'])
def initialize_vector_store():
    api_endpoint = "https://data.gov.ie/api/3/action/package_list"
    response = requests.get(api_endpoint)
    
    if response.status_code == 200:
        dataset_names = response.json().get('result', [])
        
        for name in dataset_names:
            vector = embedding_function(name)
            dataset_collection.add(name, vector)
        
        return jsonify({"message": "Dataset names initialized successfully"}), 200
    else:
        return jsonify({"error": "Failed to fetch dataset names"}), 500

def embedding_function(name):
    # Placeholder function to convert a dataset name into a vector
    return [ord(c) for c in name]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
