import React from "react";
import "./ChatWindow.css";

function ChatWindow({ messages }) {
  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={msg.user ? "user-message" : "assistant-message"}
        >
          {msg.text}
        </div>
      ))}
    </div>
  );
}

export default ChatWindow;
