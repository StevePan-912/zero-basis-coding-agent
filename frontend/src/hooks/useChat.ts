/**
 * useChat Hook
 * Chat state management with messages, mode switching, and conversation handling
 */

import { useState, useCallback } from 'react';
import { chatService } from '../services/chatService';
import type { ChatMessage, ChatMode, ChatResponse } from '../types';

interface ChatState {
  messages: ChatMessage[];
  currentMode: ChatMode;
  conversationId: number | null;
  loading: boolean;
  error: string | null;
}

interface UseChatReturn extends ChatState {
  sendMessage: (content: string) => Promise<ChatResponse | null>;
  switchMode: (mode: ChatMode) => Promise<boolean>;
  clearMessages: () => void;
  loadConversation: (conversationId: number) => Promise<void>;
  startNewConversation: (mode?: ChatMode) => Promise<number | null>;
  clearError: () => void;
}

const initialState: ChatState = {
  messages: [],
  currentMode: 'teaching',
  conversationId: null,
  loading: false,
  error: null,
};

// Helper to generate temporary IDs for optimistic updates
let tempIdCounter = 0;
const generateTempId = () => --tempIdCounter;

/**
 * Chat hook for managing messages, modes, and conversations
 */
export function useChat(): UseChatReturn {
  const [state, setState] = useState<ChatState>(initialState);

  // Send message handler
  const sendMessage = useCallback(async (content: string): Promise<ChatResponse | null> => {
    if (!content.trim()) {
      return null;
    }

    setState((prev) => ({ ...prev, loading: true, error: null }));

    // Optimistically add user message
    const userMessage: ChatMessage = {
      id: generateTempId(),
      role: 'user',
      content,
      mode: state.currentMode,
      created_at: new Date().toISOString(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
    }));

    try {
      const response = await chatService.sendMessage({
        message: content,
        mode: state.currentMode,
        conversation_id: state.conversationId ?? undefined,
      });

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: response.id,
        role: 'assistant',
        content: response.content,
        mode: response.mode,
        created_at: response.created_at,
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        conversationId: response.conversation_id,
        loading: false,
      }));

      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return null;
    }
  }, [state.currentMode, state.conversationId]);

  // Switch mode handler
  const switchMode = useCallback(async (mode: ChatMode): Promise<boolean> => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      await chatService.switchMode({ mode });
      setState((prev) => ({
        ...prev,
        currentMode: mode,
        loading: false,
      }));
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to switch mode';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return false;
    }
  }, []);

  // Clear messages handler
  const clearMessages = useCallback(() => {
    setState((prev) => ({
      ...prev,
      messages: [],
      conversationId: null,
    }));
  }, []);

  // Load conversation handler
  const loadConversation = useCallback(async (conversationId: number): Promise<void> => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await chatService.getConversationHistory(conversationId);
      const currentMode = response.items.length > 0 ? response.items[0].mode : 'teaching';

      setState({
        messages: response.items,
        currentMode,
        conversationId,
        loading: false,
        error: null,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load conversation';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  }, []);

  // Start new conversation handler
  const startNewConversation = useCallback(async (mode?: ChatMode): Promise<number | null> => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await chatService.startNewConversation(mode || state.currentMode);
      setState({
        messages: [],
        currentMode: response.mode,
        conversationId: response.id,
        loading: false,
        error: null,
      });
      return response.id;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start new conversation';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return null;
    }
  }, [state.currentMode]);

  // Clear error handler
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    sendMessage,
    switchMode,
    clearMessages,
    loadConversation,
    startNewConversation,
    clearError,
  };
}

export default useChat;