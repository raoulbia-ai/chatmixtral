"""
 simplistic embedding function currently being used. 
 The custom embedding function defined in the script is converting each character of the text into its ASCII 
 value and padding/truncating it to a fixed length. 
 This approach does not capture the semantic meaning of the text, leading to poor search results.
"""
import requests
import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define a custom embedding function
class CustomEmbeddingFunction(EmbeddingFunction):
    def __call__(self, texts):
        if not isinstance(texts, list):
            texts = [texts]
        return [self._embed(text) for text in texts]

    def _embed(self, text):
        # Ensure consistent dimension and proper format
        vector = [ord(c) for c in text]
        if len(vector) < 128:
            vector.extend([0] * (128 - len(vector)))
        return vector[:128]

# Initialize ChromaDB client and collection
client = chromadb.Client()
embedding_function = CustomEmbeddingFunction()

dataset_collection = client.get_or_create_collection(
    name='dataset_names',
    metadata={'description': 'Collection of dataset names'},
    embedding_function=embedding_function
)

# Ensure the dataset is initialized with embeddings
def initialize_chromadb():
    api_endpoint = "https://data.gov.ie/api/3/action/package_list"
    response = requests.get(api_endpoint)

    if response.status_code == 200:
        dataset_names = response.json().get('result', [])

        ids = [str(i) for i in range(len(dataset_names))]
        vectors = embedding_function(dataset_names)

        dataset_collection.add(
            ids=ids,
            documents=dataset_names,
            embeddings=vectors,
            metadatas=[{'name': name} for name in dataset_names]
        )

        logging.info("Dataset names initialized successfully at startup")
    else:
        logging.error("Failed to fetch dataset names at startup")

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

    if search_results and search_results['metadatas']:
        search_results_text = "\n".join([metadata['name'] for metadata in search_results['metadatas'][0]])
        print("Direct Search Results from ChromaDB:")
        print(search_results_text)
    else:
        print("No results found")

# Example usage
if __name__ == "__main__":
    query_text = "vocational training dataset"
    query_vector_db_direct(query_text)
