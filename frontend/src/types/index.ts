/**
 * TypeScript type definitions for the Zero Basis Coding Agent frontend
 */

// ==================== User Types ====================

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface LearningProgress {
  user_id: number;
  total_messages: number;
  concepts_learned: number;
  current_streak: number;
  last_active: string;
}

// ==================== Auth Types ====================

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
}

// ==================== Chat Types ====================

export type ChatMode = 'teaching' | 'practice' | 'creation';

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  mode: ChatMode;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  mode: ChatMode;
  conversation_id?: number;
}

export interface ChatResponse {
  id: number;
  role: 'assistant';
  content: string;
  mode: ChatMode;
  conversation_id: number;
  created_at: string;
}

export interface ModeSwitchRequest {
  mode: ChatMode;
}

export interface ModeSwitchResponse {
  previous_mode: ChatMode;
  new_mode: ChatMode;
  message: string;
}

// ==================== Content Types ====================

export interface TeachingContent {
  id: number;
  title: string;
  content: string;
  mode: ChatMode;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  created_at: string;
}

// ==================== Error Types ====================

export interface APIError {
  detail: string;
  status_code: number;
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

// ==================== API Response Wrappers ====================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}