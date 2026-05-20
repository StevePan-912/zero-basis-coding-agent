/**
 * Chat Page
 * Main chat interface combining message display, input, and mode switching
 */

import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import ModeSwitch from '../components/ModeSwitch';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';
import { useChat } from '../hooks/useChat';

function ChatPage() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  const {
    messages,
    currentMode,
    loading,
    error,
    sendMessage,
    switchMode,
    startNewConversation,
    clearError,
  } = useChat();

  // Ref for auto-scrolling to latest message
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check authentication on mount
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Initialize conversation
    startNewConversation();
  }, [isAuthenticated, navigate, startNewConversation]);

  // Auto-scroll to latest message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Send message handler
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) {
      return;
    }
    await sendMessage(content);
  };

  // Mode switch handler
  const handleModeSwitch = async (mode: string) => {
    if (mode === currentMode) {
      return;
    }
    const success = await switchMode(mode as 'teaching' | 'practice' | 'creation');
    if (success) {
      // Start a new conversation for the new mode
      await startNewConversation(mode as 'teaching' | 'practice' | 'creation');
    }
  };

  // Logout handler
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="chat-page">
      {/* Header */}
      <header className="chat-header">
        <div className="chat-header-title">
          <h1>ZerGO Coding Agent</h1>
          <span className="chat-header-subtitle">零基础编程学习助手</span>
        </div>
        <button
          type="button"
          className="chat-header-logout"
          onClick={handleLogout}
        >
          🚪 退出登录
        </button>
      </header>

      {/* Mode Switch */}
      <div className="chat-mode-container">
        <ModeSwitch currentMode={currentMode} onSwitch={handleModeSwitch} />
      </div>

      {/* Error Display */}
      {error && (
        <ErrorMessage message={error} onDismiss={clearError} />
      )}

      {/* Messages Container */}
      <main className="chat-messages">
        {loading && messages.length === 0 ? (
          <LoadingSpinner message="加载中..." />
        ) : messages.length === 0 ? (
          <div className="chat-empty">
            <h2>开始对话</h2>
            <p>发送一条消息开始与AI助手对话</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </main>

      {/* Input Area */}
      <footer className="chat-input-area">
        <ChatInput onSend={handleSendMessage} disabled={loading} />
      </footer>
    </div>
  );
}

export default ChatPage;