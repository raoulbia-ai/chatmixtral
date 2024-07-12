import React, { useState, useEffect } from "react";
import ChatWindow from "./ChatWindow";
import MessageInput from "./MessageInput";
import "./App.css";
import "./Spinner.css"; // Import the spinner CSS
import { v4 as uuidv4 } from 'uuid'; // Import UUID for session ID generation

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false); // Add loading state
  const [sessionId, setSessionId] = useState(null); // Add session ID state

  useEffect(() => {
    // Generate or retrieve session ID on component mount
    let storedSessionId = localStorage.getItem('session_id');
    if (!storedSessionId) {
      storedSessionId = uuidv4();
      localStorage.setItem('session_id', storedSessionId);
    }
    setSessionId(storedSessionId);
  }, []);

  const sendMessage = async (text) => {
    if (!sessionId) {
      console.error("No session ID found");
      return;
    }

    setLoading(true); // Set loading to true when starting to send a message
    console.log("Sending message:", text); // Debugging log

    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ session_id: sessionId, message: text }), // Send the message payload with session ID
    });

    const data = await response.json();
    console.log("Received response:", data); // Debugging log

    setLoading(false); // Set loading to false when a response is received

    if (data && data.response) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { user: true, text },
        { user: false, text: data.response },
      ]);
    } else {
      console.error("Unexpected response format:", data); // Debugging log
    }
  };

  const clearHistory = async () => {
    if (!sessionId) {
      console.error("No session ID found");
      return;
    }

    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/clear_history`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ session_id: sessionId }), // Send session ID to clear history for the current session
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
