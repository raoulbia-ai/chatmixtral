import os
import requests
from dotenv import load_dotenv
import logging
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv(dotenv_path='../backend/.env')
api_key = os.getenv('MIXTRAL_API_KEY')


user_request = 'vocational training'
search_results = """ppo08-further-education-activity-excluding-apprenticeships
ppo07-further-education-activity-nfq-level-excluding-apprenticeships
18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2020
21-22-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2020
18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2019
18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2022
18-20-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2023
21-22-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2019
21-22-years-in-receipt-of-an-aftercare-service-in-vocational-training-including-youthreach-2022 
"""

mistral_query = f"""
                 You are a powerful assistant that refines search results 

                 {search_results} based on this query: {user_request}
                 
                 """

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

# role = 'user'
# role = 'assistant'
role = 'system'

messages = [{
    'role': role, 
    'content': mistral_query
}]


mistral_client = MistralClient(api_key=api_key)
mistral_model = "mistral-large-latest"

chat_response = mistral_client.chat(
    model=mistral_model,
    messages=messages,
    temperature=0
)

mixtral_response = chat_response.choices[0].message.content
logging.info(f"Response from Mixtral: {mixtral_response}")
