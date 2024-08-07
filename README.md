DataGovIE Dataset Search Chatbot
=====================

Welcome to the DataGovIE Dataset Search Chatbot repository! This application is a proof of concept designed to provide a seamless chat experience for searching datasets available on data.gov.ie. It uses the Mixtral LLM, a language model developed by OpenAI, to generate AI responses and ChromaDB for dataset search functionality. The application uses a React frontend to provide a real-time chat interface and a Flask backend to handle API requests and manage conversation history. The current version of the application retrieves the 10 closest matches to a user's search query and provides URLs to the relevant dataset pages. Future work includes integration with a sandbox environment so that the LLM can download the data and then answer questions about it, including creating visualisations. One of the main areas to be finalised is the chat memory, allowing the user to ask follow-up questions with references to previous conversation turns.

Getting Started
---------------

**Prerequisites:**
Before diving in, make sure you have the following installed:
- Node.js (version 14 or later)
- npm (version 6 or later)
- Python 3.6 or later
- pip

**Installation:**
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the frontend dependencies by running `npm install`.
4. Navigate to the backend directory and install the backend dependencies by running `pip install -r requirements.txt`.
5. If encountering errors when trying to start frontend, use `npm install react-scripts@latest`.

Running the Application
-----------------------

To start the development server, execute `npm start` in the frontend directory. This compiles the application and launches it in your default web browser at `http://localhost:3000`.

To start the backend server, navigate to the backend directory and run `python app.py`.

Building for Production
-----------------------

For production builds, run [`npm run build`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Fhome%2Fraoulbia%2Frepos%2Fwp-chatmixtral%2Ffrontend%2FREADME.md%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A29%2C%22character%22%3A0%7D%5D "frontend/README.md"). This command prepares optimized assets in the [`build`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Fhome%2Fraoulbia%2Frepos%2Fwp-chatmixtral%2Ffrontend%2FREADME.md%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A29%2C%22character%22%3A0%7D%5D "frontend/README.md") directory, ready for deployment.

Testing
-------

For local testing, initiate the application with `npm start`. To ensure a clean state, clear the browser's local and session storage by executing `localStorage.clear(); sessionStorage.clear(); location.reload();` in the browser console.

Deployment
----------

For detailed instructions on deploying the application to various platforms, refer to the [Create React App deployment documentation](https://facebook.github.io/create-react-app/docs/deployment).

Contributing
------------

We welcome contributions! If you're interested in helping improve ChatMixtral, please read our contributing guidelines first.

License
-------

This project is licensed under the MIT License. See the LICENSE file in the repository for more details.
