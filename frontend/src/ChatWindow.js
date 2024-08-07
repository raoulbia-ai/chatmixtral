import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import './ChatWindow.css';

const ChatWindow = ({ messages }) => (
  <div className="chat-window">
    <div className="chat-history">
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.user ? 'user' : 'ai'}`}>
          <span>{msg.user ? 'User' : 'AI'}:</span>
          <div className="message-content">
            <ReactMarkdown rehypePlugins={[rehypeRaw]}>{msg.text}</ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default ChatWindow;
