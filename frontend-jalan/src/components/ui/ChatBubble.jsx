import React from 'react';
import './ChatBubble.css';

const ChatBubble = ({ message, sender = 'ai', timestamp, isTyping = false }) => {
  if (isTyping) {
    return (
      <div className="chat-bubble chat-bubble-ai">
        <div className="chat-avatar">🤖</div>
        <div className="chat-content">
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`chat-bubble chat-bubble-${sender}`}>
      {sender === 'ai' && <div className="chat-avatar">🤖</div>}
      <div className="chat-content">
        <div className="chat-message" dangerouslySetInnerHTML={{ __html: formatMessage(message) }} />
        {timestamp && <span className="chat-time">{timestamp}</span>}
      </div>
      {sender === 'user' && <div className="chat-avatar chat-avatar-user">👤</div>}
    </div>
  );
};

function formatMessage(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
    .replace(/- \[([A-Z]+\d+)\]/g, '<span class="data-id">[$1]</span>')
    .replace(/Rp\s*([\d.,]+)/g, '<span class="price-highlight">Rp $1</span>');
}

export default ChatBubble;
