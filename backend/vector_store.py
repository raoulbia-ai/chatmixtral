import chromadb, os, logging, pickle, requests
from chromadb.utils.embedding_functions import EmbeddingFunction
from sentence_transformers import SentenceTransformer

# Define the model to use for embeddings
EMBEDDING_MODEL = 'paraphrase-MiniLM-L6-v2'

class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name=EMBEDDING_MODEL, batch_size=32):
        self.model = SentenceTransformer(model_name)
        self.batch_size = batch_size

    def __call__(self, texts):
        if not isinstance(texts, list):
            texts = [texts]
        return self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=True).tolist()

CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# File to store embeddings
EMBEDDINGS_FILE = os.path.join(CACHE_DIR, "dataset_embeddings.pkl")


        
class VectorStore:
    def __init__(self):
        self.client = chromadb.Client()
        self.embedding_function = CustomEmbeddingFunction()  # Initialize the embedding function
        self.collection = self.client.get_or_create_collection(
                                name='dataset_names',
                                metadata={'description': 'Collection of dataset names'},
                                embedding_function=self.embedding_function
                            )
        self.initialize_chromadb()

    # Ensure the dataset is initialized with embeddings
    def initialize_chromadb(self):
        if os.path.exists(EMBEDDINGS_FILE):
            logging.info("Loading existing embeddings from file.")
            with open(EMBEDDINGS_FILE, 'rb') as f:
                ids, dataset_names, vectors, metadatas = pickle.load(f)
                self.collection.add(
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
                vectors = self.embedding_function(dataset_names)
                metadatas = [{'name': name} for name in dataset_names]

                # Save embeddings to file
                with open(EMBEDDINGS_FILE, 'wb') as f:
                    pickle.dump((ids, dataset_names, vectors, metadatas), f)
                
                # Add embeddings to ChromaDB collection
                self.collection.add(
                    ids=ids,
                    documents=dataset_names,
                    embeddings=vectors,
                    metadatas=metadatas
                )
            else:
                logging.error("Failed to fetch dataset names at startup")
                return
        



    def query_embeddings(self, user_message, n_results=10):
    # Check if the user message is a dataset query
        query_vector = self.embedding_function(user_message)[0]  # Ensure the embedding is correctly extracted

        
        search_results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        

        search_results_text = "\n".join([metadata['name'] for metadata in search_results['metadatas'][0]])
        return search_results_text


