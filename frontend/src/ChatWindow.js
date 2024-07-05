import React from 'react';
import './ChatWindow.css';

const ChatWindow = ({ messages }) => (
  <div className="chat-window">
    <div className="chat-history">
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.user ? 'user' : 'ai'}`}>
          <span>{msg.user ? 'User' : 'AI'}:</span> {msg.text}
        </div>
      ))}
    </div>
  </div>
);

export default ChatWindow;
