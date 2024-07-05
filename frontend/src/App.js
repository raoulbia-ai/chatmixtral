import React, { useState } from "react";
import ChatWindow from "./ChatWindow";
import MessageInput from "./MessageInput";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (text) => {
    console.log("Sending message:", text); // Debugging log
    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: text }),
    });

    const data = await response.json();
    console.log("Received response:", data); // Debugging log

    // Check if the response contains the expected data
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
      </header>
      <ChatWindow messages={messages} />
      <MessageInput sendMessage={sendMessage} />
    </div>
  );
}

export default App;
