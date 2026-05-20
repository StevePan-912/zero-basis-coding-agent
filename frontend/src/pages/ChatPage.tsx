/**
 * Chat Page
 * Main chat interface combining message display, input, and mode switching
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import ModeSwitch from '../components/ModeSwitch';
import authService from '../services/authService';
import chatService from '../services/chatService';
import type { ChatMessage as ChatMessageType, ChatMode } from '../types';

function ChatPage() {
  const navigate = useNavigate();

  // State management
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [currentMode, setCurrentMode] = useState<ChatMode>('teaching');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);

  // Ref for auto-scrolling to latest message
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check authentication on mount
  useEffect(() => {
    if (!authService.isAuthenticated()) {
      navigate('/login');
      return;
    }

    // Load current mode and initialize conversation
    const initializeChat = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Get current mode
        const modeResponse = await chatService.getCurrentMode();
        setCurrentMode(modeResponse.mode);

        // Start a new conversation
        const conversation = await chatService.startNewConversation(modeResponse.mode);
        setConversationId(conversation.id);
      } catch (err) {
        console.error('Failed to initialize chat:', err);
        setError('初始化聊天失败，请刷新页面重试');
      } finally {
        setIsLoading(false);
      }
    };

    initializeChat();
  }, [navigate]);

  // Auto-scroll to latest message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Send message handler
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isSending) {
      return;
    }

    setIsSending(true);
    setError(null);

    // Create user message locally for immediate display
    const userMessage: ChatMessageType = {
      id: Date.now(), // Temporary ID
      role: 'user',
      content: content.trim(),
      mode: currentMode,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      // Send message to backend
      const response = await chatService.sendMessage({
        message: content.trim(),
        mode: currentMode,
        conversation_id: conversationId ?? undefined,
      });

      // Update conversation ID if this is a new conversation
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to messages
      const assistantMessage: ChatMessageType = {
        id: response.id,
        role: 'assistant',
        content: response.content,
        mode: response.mode,
        created_at: response.created_at,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('发送消息失败，请重试');
      // Remove the optimistically added user message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
    } finally {
      setIsSending(false);
    }
  };

  // Mode switch handler
  const handleModeSwitch = async (mode: ChatMode) => {
    if (mode === currentMode) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await chatService.switchMode({ mode });
      setCurrentMode(mode);

      // Start a new conversation for the new mode
      const conversation = await chatService.startNewConversation(mode);
      setConversationId(conversation.id);
      setMessages([]); // Clear messages for new mode
    } catch (err) {
      console.error('Failed to switch mode:', err);
      setError('切换模式失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // Logout handler
  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <div className="chat-page">
      {/* Header */}
      <header className="chat-header">
        <div className="chat-header-title">
          <h1>零基础编程助手</h1>
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
        <div className="chat-error">
          {error}
          <button
            type="button"
            className="chat-error-dismiss"
            onClick={() => setError(null)}
          >
            ✖
          </button>
        </div>
      )}

      {/* Messages Container */}
      <main className="chat-messages">
        {isLoading && messages.length === 0 ? (
          <div className="chat-loading">
            <div className="chat-loading-spinner" />
            <p>加载中...</p>
          </div>
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
        <ChatInput onSend={handleSendMessage} disabled={isSending || isLoading} />
      </footer>
    </div>
  );
}

export default ChatPage;