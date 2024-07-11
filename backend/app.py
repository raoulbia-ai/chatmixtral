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

@app.route('/api/search', methods=['POST'])
def search():
    user_query = request.json.get('query')
    if not user_query:
        abort(400, description='Query is required')

    logging.info(f"Received search query: {user_query}")

    query_vector = embedding_function(user_query)[0]  # Ensure the embedding is correctly extracted

    try:
        # Using the correct method for querying the collection
        search_results = dataset_collection.query(
            query_embeddings=[query_vector],
            n_results=10
        )

        search_results_text = "\n".join([metadata['name'] for metadata in search_results['metadatas'][0]])
        logging.info(f"Search results text datatype: {type(search_results_text)}")

        # Ensure the last message is from the user or a tool
        user_query = f"{user_query}"
        mistral_query = f"""Summarize the available datasets related to {user_request} 
                            on the data.gov.ie website from the provided list. 
                            If the list is empty or no relevant datasets are found, 
                            indicate that no datasets were found.

                            Example Datasets:
                            
                            18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2020
                            21-22-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2020
                            18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2019


                            Example Query: "vocational training datasets"

                            Response:
                            - **18-20 years in receipt of an aftercare service in vocational training including Youthreach 2020**: [Link](https://data.gov.ie/dataset/18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2020)
                            - **21-22 years in receipt of an aftercare service in vocational training including Youthreach 2020**: [Link](https://data.gov.ie/dataset/21-22-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2020)
                            - **18-20 years in receipt of an aftercare service in vocational training including Youthreach 2019**: [Link](https://data.gov.ie/dataset/18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2019)
                            """
        
        role = 'system'

        messages = [{
            'role': role, 
            'content': mistral_query
        }]

        chat_response = mistral_client.chat(
            model=mistral_model,
            messages=messages
        )
        refined_response = chat_response.choices[0].message.content

        logging.info(f"Refined response from Mistral: {refined_response}")
    except Exception as e:
        logging.error(f"Failed to get response from Mistral API: {str(e)}")
        raise MixtralAPIError(f"Failed to get response from Mistral API: {str(e)}") from e

    return jsonify({'response': refined_response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
