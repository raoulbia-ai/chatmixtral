import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_caching import Cache
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv
import logging

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


@app.route('/')
def home():
    return "Welcome to the Mixtral Chatbot!"

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello from Flask!'})
    
@app.route('/api/chat', methods=['POST'])
# @cache.cached(timeout=60)
def chat():
    user_message = request.json.get('message')
    if not user_message:
        abort(400, description='Message is required')

    # Log the received message from the frontend
    logging.info(f"Received message from frontend: {user_message}")

    try:
        chat_response = mistral_client.chat(
            model=mistral_model,
            messages=[ChatMessage(role="user", content=user_message)],
        )
        mixtral_response = chat_response.choices[0].message.content

        # Log the response received from Mixtral
        logging.info(f"Response from Mixtral: {mixtral_response}")
    except Exception as e:
        logging.error(f"Failed to get response from Mixtral API: {str(e)}")
        raise MixtralAPIError(
            f"Failed to get response from Mixtral API: {str(e)}") from e

    return jsonify({'response': mixtral_response})


if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)

    # uncomment below, run script, then ctrl+c to exit which will run the test
    # # Test code to run the script in isolation and test Mixtral response
    # def test_mixtral_response():
    #     test_message = "Hello, Mixtral!"
    #     try:
    #         chat_response = mistral_client.chat(
    #             model=mistral_model,
    #             messages=[ChatMessage(role="user", content=test_message)],
    #         )
    #         mixtral_response = chat_response.choices[0].message.content
    #         print(f"Test message to Mixtral: {test_message}")
    #         print(f"Response from Mixtral: {mixtral_response}")
    #         return True
    #     except Exception as e:
    #         print(f"Failed to get response from Mixtral API: {str(e)}")
    #         return False

    # # Only run the test when this script is executed, not on import
    # if __name__ == '__main__':
    #     print("Running Mixtral response test...")
    #     test_successful = test_mixtral_response()
    #     if test_successful:
    #         print("Mixtral response test passed.")
    #     else:
    #         print("Mixtral response test failed.")