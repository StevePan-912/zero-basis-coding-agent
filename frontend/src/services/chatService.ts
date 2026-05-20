/**
 * Chat service
 * Handles chat messages, mode switching, and conversation management
 */

import { api } from './api';
import type {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  ModeSwitchRequest,
  ModeSwitchResponse,
  ChatMode,
  PaginatedResponse
} from '../types';

const CHAT_BASE_URL = '/api/v1/chat';

export const chatService = {
  /**
   * Send a chat message
   */
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    return api.post<ChatResponse>(`${CHAT_BASE_URL}/message`, data);
  },

  /**
   * Switch chat mode (teaching, practice, creation)
   */
  async switchMode(data: ModeSwitchRequest): Promise<ModeSwitchResponse> {
    return api.post<ModeSwitchResponse>(`${CHAT_BASE_URL}/mode`, data);
  },

  /**
   * Get current chat mode
   */
  async getCurrentMode(): Promise<{ mode: ChatMode }> {
    return api.get<{ mode: ChatMode }>(`${CHAT_BASE_URL}/mode`);
  },

  /**
   * Get conversation history
   */
  async getConversationHistory(
    conversationId: number,
    page: number = 1,
    pageSize: number = 50
  ): Promise<PaginatedResponse<ChatMessage>> {
    return api.get<PaginatedResponse<ChatMessage>>(
      `${CHAT_BASE_URL}/conversations/${conversationId}`,
      {
        params: {
          page,
          page_size: pageSize,
        },
      }
    );
  },

  /**
   * Get all conversations for current user
   */
  async getConversations(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<{ id: number; mode: ChatMode; created_at: string }>> {
    return api.get<PaginatedResponse<{ id: number; mode: ChatMode; created_at: string }>>(
      `${CHAT_BASE_URL}/conversations`,
      {
        params: {
          page,
          page_size: pageSize,
        },
      }
    );
  },

  /**
   * Start a new conversation
   */
  async startNewConversation(mode: ChatMode): Promise<{ id: number; mode: ChatMode }> {
    return api.post<{ id: number; mode: ChatMode }>(`${CHAT_BASE_URL}/conversations`, { mode });
  },

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: number): Promise<void> {
    await api.delete(`${CHAT_BASE_URL}/conversations/${conversationId}`);
  },
};

export default chatService;