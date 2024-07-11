import requests
import json

# Define the base URL for the API
BASE_URL = "http://localhost:5000"

# Define the search endpoint
SEARCH_ENDPOINT = f"{BASE_URL}/api/search"

# Define a function to query the vector database
def query_vector_db(query_text):
    payload = {
        "query": query_text
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(SEARCH_ENDPOINT, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Search Results:")
        print(data['response'])
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Example usage
if __name__ == "__main__":
    query_text = "example dataset query"
    query_vector_db(query_text)
