/**
 * useAuth Hook
 * Authentication state management with login, register, logout
 */

import { useState, useCallback, useEffect } from 'react';
import { authService } from '../services/authService';
import type { LoginRequest, RegisterRequest, AuthResponse } from '../types';

interface AuthState {
  isAuthenticated: boolean;
  userId: number | null;
  username: string | null;
  loading: boolean;
  error: string | null;
}

interface UseAuthReturn extends AuthState {
  login: (data: LoginRequest) => Promise<AuthResponse | null>;
  register: (data: RegisterRequest) => Promise<AuthResponse | null>;
  logout: () => void;
  clearError: () => void;
}

const initialState: AuthState = {
  isAuthenticated: false,
  userId: null,
  username: null,
  loading: false,
  error: null,
};

/**
 * Authentication hook for managing user auth state
 */
export function useAuth(): UseAuthReturn {
  const [state, setState] = useState<AuthState>(initialState);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const isAuth = authService.isAuthenticated();
    const userId = authService.getCurrentUserId();

    setState((prev) => ({
      ...prev,
      isAuthenticated: isAuth,
      userId: isAuth ? userId : null,
    }));
  }, []);

  // Login handler
  const login = useCallback(async (data: LoginRequest): Promise<AuthResponse | null> => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await authService.login(data);
      setState({
        isAuthenticated: true,
        userId: response.user_id,
        username: response.username,
        loading: false,
        error: null,
      });
      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return null;
    }
  }, []);

  // Register handler
  const register = useCallback(async (data: RegisterRequest): Promise<AuthResponse | null> => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await authService.register(data);
      setState({
        isAuthenticated: true,
        userId: response.user_id,
        username: response.username,
        loading: false,
        error: null,
      });
      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return null;
    }
  }, []);

  // Logout handler
  const logout = useCallback(() => {
    authService.logout();
    setState({
      isAuthenticated: false,
      userId: null,
      username: null,
      loading: false,
      error: null,
    });
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    login,
    register,
    logout,
    clearError,
  };
}

export default useAuth;