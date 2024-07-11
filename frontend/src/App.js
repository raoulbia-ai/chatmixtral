import React, { useState } from "react";
import ChatWindow from "./ChatWindow";
import MessageInput from "./MessageInput";
import "./App.css";
import "./Spinner.css"; // Import the spinner CSS

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false); // Add loading state

  const sendMessage = async (text) => {
    setLoading(true); // Set loading to true when starting to send a message
    console.log("Sending message:", text); // Debugging log

    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: text }), // Send the message payload
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

  const clearHistory = async () => {
    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/clear_history`, {
      method: "POST",
    });

    const data = await response.json();
    console.log(data.message); // Debugging log
    setMessages([]); // Clear messages in the frontend
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>ChatMixtral App</h1>
        <p>Welcome to the ChatMixtral App! Type your message below and chat with our AI.</p>
      </header>
      {loading && <div className="spinner"></div>} {/* Show spinner when loading */}
      <ChatWindow messages={messages} />
      <MessageInput sendMessage={sendMessage} clearHistory={clearHistory} />
    </div>
  );
}

export default App;
