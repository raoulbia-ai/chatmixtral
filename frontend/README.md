# ChatMixtral

Welcome to the ChatMixtral repository! This project is an innovative chat application designed to deliver a seamless chat experience powered by the Mixtral LLM. Utilizing React for the frontend and Python Flask for the backend, ChatMixtral offers a minimalistic yet powerful UI for real-time messaging.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:
- Node.js (version 14 or later)
- npm (version 6 or later)
- Python (version 3.7 or later)

### Installation

Follow these steps to get your development environment set up:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the necessary dependencies for the frontend:
   ```sh
   cd frontend
   npm install
   ```
   If you encounter any errors, try updating [`react-scripts`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2Fhome%2Fraoulbia%2Frepos%2Fwp-chatmixtral%2Ffrontend%2Fnode_modules%2F%40types%2Freact%2Findex.d.ts%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A6%2C%22character%22%3A0%7D%5D "frontend/node_modules/@types/react/index.d.ts"):
   ```sh
   npm install react-scripts@latest
   ```
4. Install the necessary dependencies for the backend:
   ```sh
   cd ../backend
   pip install -r requirements.txt
   ```

## Running the Application

To run the application locally:

1. Start the backend server:
   ```sh
   cd backend
   python app.py
   ```
2. In a new terminal, start the frontend development server:
   ```sh
   cd frontend
   npm start
   ```
   This will compile the application and launch it in your default web browser at `http://localhost:3000`.

## Building for Production

To create a production build of the frontend:
