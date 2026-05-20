/**
 * ChatInput Component
 * Input field for sending chat messages
 */

import { useState, FormEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Don't send empty or whitespace-only messages
    const trimmedMessage = message.trim();
    if (!trimmedMessage || disabled) {
      return;
    }

    onSend(trimmedMessage);
    setMessage(''); // Clear input after sending
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const trimmedMessage = message.trim();
      if (trimmedMessage && !disabled) {
        onSend(trimmedMessage);
        setMessage('');
      }
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="chat-input-container">
        <textarea
          className="chat-input-textarea"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入消息... (Enter发送, Shift+Enter换行)"
          disabled={disabled}
          rows={1}
        />
        <button
          type="submit"
          className="chat-input-send"
          disabled={disabled || !message.trim()}
        >
          {disabled ? '⏳' : '🚀'}
        </button>
      </div>
    </form>
  );
}

export default ChatInput;