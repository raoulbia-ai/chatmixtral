import React, { useState } from 'react';
import './MessageInput.css';

const MessageInput = ({ sendMessage }) => {
  const [message, setMessage] = useState('');

  const handleSendMessage = () => {
    if (message.trim()) {
      console.log("Message input:", message); // Debugging log
      sendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="message-input">
      <input 
        type="text" 
        value={message} 
        onChange={(e) => setMessage(e.target.value)} 
        onKeyPress={handleKeyPress} 
        placeholder="Type your message here..." 
      />
      <button onClick={handleSendMessage}>Send</button>
    </div>
  );
};

export default MessageInput;
