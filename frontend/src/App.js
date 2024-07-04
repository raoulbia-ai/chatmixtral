import React, { useState } from "react";
import ChatWindow from "./ChatWindow";
import MessageInput from "./MessageInput";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (text) => {
    // Send message to backend and receive response
    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: text }),
    });
    const data = await response.json();
    // Update messages with user message and response
    setMessages([
      ...messages,
      { user: true, text },
      { user: false, text: data.response },
    ]);
  };

  return (
    <div className="App">
      <ChatWindow messages={messages} />
      <MessageInput sendMessage={sendMessage} />
    </div>
  );
}

export default App;
