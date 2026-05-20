/**
 * ChatMessage Component
 * Displays individual chat messages with role icons and timestamps
 */

import type { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  // Format timestamp to readable string
  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={`chat-message ${isUser ? 'chat-message-user' : 'chat-message-assistant'}`}>
      <div className="chat-message-header">
        <span className="chat-message-role">
          {isUser ? '👤' : '🤖'} {isUser ? '你' : 'AI助手'}
        </span>
        <span className="chat-message-time">
          {formatTime(message.created_at)}
        </span>
      </div>
      <div className="chat-message-content">
        {message.content}
      </div>
    </div>
  );
}

export default ChatMessage;