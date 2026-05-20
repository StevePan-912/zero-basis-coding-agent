/**
 * Authentication service
 * Handles user registration, login, logout, and auth state
 */

import { api, authStorage } from './api';
import type { RegisterRequest, LoginRequest, AuthResponse, User } from '../types';

const AUTH_BASE_URL = '/api/v1/auth';

export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(`${AUTH_BASE_URL}/register`, data);

    // Store auth data
    authStorage.setToken(response.access_token);
    authStorage.setUserId(response.user_id);

    return response;
  },

  /**
   * Login user and store token
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(`${AUTH_BASE_URL}/login`, data);

    // Store auth data
    authStorage.setToken(response.access_token);
    authStorage.setUserId(response.user_id);

    return response;
  },

  /**
   * Logout user - clear stored auth data
   */
  logout(): void {
    authStorage.clear();
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!authStorage.getToken();
  },

  /**
   * Get current user ID
   */
  getCurrentUserId(): number | null {
    return authStorage.getUserId();
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    return api.get<User>(`${AUTH_BASE_URL}/me`);
  },
};

export default authService;