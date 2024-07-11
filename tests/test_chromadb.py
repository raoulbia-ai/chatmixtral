import pytest
import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction

# Define a custom embedding function for tests
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

# Initialize the ChromaDB client and collection for tests
@pytest.fixture(scope='module')
def chromadb_setup():
    client = chromadb.Client()
    embedding_function = CustomEmbeddingFunction()
    collection = client.get_or_create_collection(
        name='test_dataset_names',
        metadata={'description': 'Test collection of dataset names'},
        embedding_function=embedding_function
    )
    return client, collection, embedding_function

def test_add_documents(chromadb_setup):
    client, collection, embedding_function = chromadb_setup

    # Test data
    dataset_names = ["test_dataset_1", "test_dataset_2"]
    ids = [str(i) for i in range(len(dataset_names))]
    vectors = embedding_function(dataset_names)

    # Add documents to the collection
    collection.add(
        ids=ids,
        documents=dataset_names,
        embeddings=vectors,
        metadatas=[{'name': name} for name in dataset_names]
    )

    # Check if documents are added correctly
    results = collection.get(ids=ids)
    assert len(results['documents']) == 2
    assert results['documents'][0] == "test_dataset_1"
    assert results['documents'][1] == "test_dataset_2"

def test_query_documents(chromadb_setup):
    client, collection, embedding_function = chromadb_setup

    # Test query
    query = "test_dataset_1"
    query_vector = embedding_function(query)[0]  # Get the first (and only) embedding

    # Query the collection
    search_results = collection.query(
        query_embeddings=[query_vector],
        n_results=1
    )

    # Extract the document names from the search results
    document_names = [result['name'] for result in search_results['metadatas'][0]]

    # Check if the query returns the expected document
    assert len(document_names) == 1
    assert document_names[0] == "test_dataset_1"

if __name__ == "__main__":
    pytest.main()
