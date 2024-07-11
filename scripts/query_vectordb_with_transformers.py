import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
from sentence_transformers import SentenceTransformer
import logging
import requests
import os
import pickle

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the model to use for embeddings
EMBEDDING_MODEL = 'paraphrase-MiniLM-L6-v2'
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

# Define a function to query the vector database directly
def query_vector_db_direct(query_text):
    logging.debug(f"Query Text: {query_text}")
    
    query_vector = embedding_function(query_text)[0]  # Ensure the embedding is correctly extracted
    logging.debug(f"Query Vector: {query_vector}")

    # Using the correct method for querying the collection
    search_results = dataset_collection.query(
        query_embeddings=[query_vector],
        n_results=10
    )

    logging.debug(f"Search Results: {search_results}")

    if search_results and search_results['metadatas'][0]:
        search_results_text = "\n".join([metadata['name'] for metadata in search_results['metadatas'][0]])
        print("Direct Search Results from ChromaDB:")
        print(search_results_text)
    else:
        print("No results found")

# Example usage
if __name__ == "__main__":
    query_text = "vocational training dataset"
    query_vector_db_direct(query_text)
