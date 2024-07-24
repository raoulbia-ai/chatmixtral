import os
import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_caching import Cache
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv
import logging
import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
from sentence_transformers import SentenceTransformer
import requests
import sqlite3
import pickle
from prompts.roles import system, user
from langchain.memory import ConversationBufferMemory  # Import LangChain memory

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

# Define the model to use for embeddings
EMBEDDING_MODEL = 'paraphrase-MiniLM-L6-v2'

# Define a custom embedding function using SentenceTransformers
class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name=EMBEDDING_MODEL, batch_size=32):
        self.model = SentenceTransformer(model_name)
        self.batch_size = batch_size
    
    def __call__(self, texts):
        if not isinstance(texts, list):
            texts = [texts]
        return self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=True).tolist()

# Initialize ConversationBufferMemory
memory = ConversationBufferMemory()

# Initialize ChromaDB client and collection
client = chromadb.Client()
embedding_function = CustomEmbeddingFunction()

dataset_collection = client.get_or_create_collection(
    name='dataset_names',
    metadata={'description': 'Collection of dataset names'},
    embedding_function=embedding_function
)

CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# File to store embeddings
EMBEDDINGS_FILE = os.path.join(CACHE_DIR, "dataset_embeddings.pkl")

# Ensure the dataset is initialized with embeddings
def initialize_chromadb():
    if os.path.exists(EMBEDDINGS_FILE):
        logging.info("Loading existing embeddings from file.")
        with open(EMBEDDINGS_FILE, 'rb') as f:
            ids, dataset_names, vectors, metadatas = pickle.load(f)
            dataset_collection.add(
                ids=ids,
                documents=dataset_names,
                embeddings=vectors,
                metadatas=metadatas
            )
    else:
        logging.info("Computing embeddings and storing them in file.")
        api_endpoint = "https://data.gov.ie/api/3/action/package_list"
        response = requests.get(api_endpoint)

        if response.status_code == 200:
            dataset_names = response.json().get('result', [])
            ids = [str(i) for i in range(len(dataset_names))]
            vectors = embedding_function(dataset_names)
            metadatas = [{'name': name} for name in dataset_names]

            # Save embeddings to file
            with open(EMBEDDINGS_FILE, 'wb') as f:
                pickle.dump((ids, dataset_names, vectors, metadatas), f)
            
            # Add embeddings to ChromaDB collection
            dataset_collection.add(
                ids=ids,
                documents=dataset_names,
                embeddings=vectors,
                metadatas=metadatas
            )
        else:
            logging.error("Failed to fetch dataset names at startup")
            return

initialize_chromadb()

@app.route('/')
def home():
    return "Welcome to the Mixtral Chatbot!"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    logging.info(f"User message: {user_message}")
    session_id = data.get('session_id')
    logging.info(f"Session ID: {session_id}")
        
    if not user_message or not session_id:
        return jsonify({'error': 'Message and session_id are required'}), 400

    try:
        # Add user message to memory
        memory.chat_memory.add_user_message(user_message)
        logging.info(f"Added user message to memory: {memory.load_memory_variables({})}")           

        query_vector = embedding_function(user_message)[0]  # Ensure the embedding is correctly extracted

        n_results = 10
        
        search_results = dataset_collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )

        search_results_text = "\n".join([metadata['name'] for metadata in search_results['metadatas'][0]])
        logging.info(f"Search results text datatype: {type(search_results_text)}")
    
        # Create the user prompt
        user_prompt = user.format(user_message = user_message,
                                  conv_history = memory.load_memory_variables({})['history'],
                                  n_results = n_results,
                                  search_results_text = search_results_text)
        
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
