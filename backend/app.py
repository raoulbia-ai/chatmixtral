import os
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

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello from Flask!'})

# Database setup for storing conversation history
CHAT_HISTORY_DIR = os.getenv('CHAT_HISTORY_DIR', os.path.join(os.path.dirname(__file__), 'chat_history'))
CHAT_HISTORY_DB = os.path.join(CHAT_HISTORY_DIR, 'chat_history.db')

if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)

def init_db():
    conn = sqlite3.connect(CHAT_HISTORY_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_conversation_history(session_id):
    conn = sqlite3.connect(CHAT_HISTORY_DB)
    c = conn.cursor()
    c.execute('SELECT role, content FROM conversation_history WHERE session_id = ?', (session_id,))
    history = c.fetchall()
    conn.close()
    return [{'role': row[0], 'content': row[1]} for row in history]

def add_to_conversation_history(session_id, role, content):
    conn = sqlite3.connect(CHAT_HISTORY_DB)
    c = conn.cursor()
    c.execute('INSERT INTO conversation_history (session_id, role, content) VALUES (?, ?, ?)', (session_id, role, content))
    conn.commit()
    conn.close()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')

    if not session_id or not user_message:
        return jsonify({'error': 'session_id and message are required'}), 400

    logging.info(f"Received message from frontend: {user_message}")

    # Get conversation history
    conversation_history = get_conversation_history(session_id)

    # Update conversation history
    conversation_history.append({'role': 'user', 'content': user_message})
    add_to_conversation_history(session_id, 'user', user_message)

    # Prepare the Mistral query
    check_query = f"""Does the user query '{user_message}' relate to a dataset, 
                      or does it relate to a previously asked question in the conversation history: {conversation_history}?
                      You may only respond with one of two words: "yes" or "no".
                      Do not use punctuation in your response!
                      
                      Example:
                      ========
                      Question: What is the weather in Dublin
                      Response: No

                      Example
                      ========
                      Question: What datasets are available on data.gov.ie?
                      Response: Yes
                      
                      Response:
                    """

    messages = [
        {'role': 'system', 'content': check_query}
    ]

    chat_response = mistral_client.chat(
        model=mistral_model,
        messages=messages
    )
    refined_response = chat_response.choices[0].message.content
    logging.info(f"Refined response from Mistral: {refined_response}")

    if refined_response.lower() == "no":
        # Prepare the Mistral query
        general_query = f"""{user_message}"""

        messages = [
            {'role': 'user', 'content': general_query}
        ]

        chat_response = mistral_client.chat(
            model=mistral_model,
            messages=messages
        )
        general_response = chat_response.choices[0].message.content
        logging.info(f"General response from Mistral: {general_response}")

        # Update conversation history
        add_to_conversation_history(session_id, 'assistant', general_response)

        return jsonify({'response': general_response})
    
    else:
        try:
            # Check if the user message is a dataset query
            query_vector = embedding_function(user_message)[0]  # Ensure the embedding is correctly extracted

            n_results = 10
            search_results = dataset_collection.query(
                query_embeddings=[query_vector],
                n_results=n_results
            )

            search_results_text = "\n".join([metadata['name'] for metadata in search_results['metadatas'][0]])
            logging.info(f"Search results text datatype: {type(search_results_text)}")

            # Prepare the Mistral query
            mistral_query = f"""List the available datasets related to '{user_message}' 
                                on the data.gov.ie website from the provided list of these {n_results} datasets: 
                                {search_results_text}. 

                                If the list is empty or no relevant datasets were found, 
                                indicate that no datasets were found.

                                Response format should be an intro text followed by a bullet list of available datasets names.
                                Use friendly names in bold. Do not add any speculative comments such as "It may contain ...".
                                Instead, provide the URL to the dataset by prepending it with https://data.gov.ie/dataset/.

                                Example Output
                                ==============
                                Intro text: Here are some datasets related to your query:<br>
                                <a href="https://data.gov.ie/dataset/my-example-dataset-name" target="_blank">My Example Dataset Name</a>

                                Response:
                                """

            messages = [
                {'role': 'system', 'content': mistral_query}
            ]

            chat_response = mistral_client.chat(
                model=mistral_model,
                messages=messages
            )
            refined_response = chat_response.choices[0].message.content

            # Update conversation history
            add_to_conversation_history(session_id, 'assistant', refined_response)

            logging.info(f"Refined response from Mistral: {refined_response}")

            logging.info(f"Conversation history: {conversation_history}")
            
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

    conn = sqlite3.connect(CHAT_HISTORY_DB)
    c = conn.cursor()
    c.execute('DELETE FROM conversation_history WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

    logging.info(f"Conversation history cleared for session: {session_id}")
    return jsonify({'message': 'Conversation history cleared'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
