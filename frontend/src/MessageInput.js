import React, { useState } from "react";
import "./MessageInput.css";

const MessageInput = ({ sendMessage, clearHistory }) => {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim() !== "") {
      sendMessage(text);
      setText("");
    }
  };

  return (
    <div className="message-input-container">
      <div className="message-input">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter") handleSend();
          }}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
        <button onClick={clearHistory}>Clear History</button>
      </div>
    </div>
  );
};

export default MessageInput;
