import React, { useState } from "react";
import ChatWindow from "./ChatWindow";
import MessageInput from "./MessageInput";
import "./App.css";
import "./Spinner.css"; // Import the spinner CSS

function App() {
  const [messages, setMessages] = useState([]);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [loading, setLoading] = useState(false); // Add loading state

  const sendMessage = async (text) => {
    setLoading(true); // Set loading to true when starting to send a message
    console.log("Sending message:", text); // Debugging log

    const endpoint = isSearchMode ? "api/search" : "api/chat";
    const payload = isSearchMode ? { query: text } : { message: text };
    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload), // Send as 'query' for search endpoint
    });

    const data = await response.json();
    console.log("Received response:", data); // Debugging log

    setLoading(false); // Set loading to false when a response is received

    if (data && data.response) {
      setMessages([
        ...messages,
        { user: true, text },
        { user: false, text: data.response },
      ]);
    } else {
      console.error("Unexpected response format:", data); // Debugging log
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>ChatMixtral App</h1>
        <p>Welcome to the ChatMixtral App! Type your message below and chat with our AI.</p>
        <div>
          <button 
            onClick={() => setIsSearchMode(false)} 
            style={{ backgroundColor: !isSearchMode ? 'blue' : 'gray', color: 'white' }}
          >
            Chat Mode
          </button>
          <button 
            onClick={() => setIsSearchMode(true)} 
            style={{ backgroundColor: isSearchMode ? 'blue' : 'gray', color: 'white' }}
          >
            Search Mode
          </button>
        </div>
      </header>
      {loading && <div className="spinner"></div>} {/* Show spinner when loading */}
      <ChatWindow messages={messages} />
      <MessageInput sendMessage={sendMessage} />
    </div>
  );
}

export default App;
