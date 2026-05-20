/**
 * Login Page
 * Handles user login with AuthForm component
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import authService from '../services/authService';
import type { LoginRequest } from '../types';

function LoginPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (data: LoginRequest) => {
    setError(null);
    try {
      await authService.login(data);
      // Login successful, navigate to chat page
      navigate('/chat');
    } catch (err) {
      // Handle error
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('登录失败，请检查用户名和密码');
      }
    }
  };

  return (
    <div className="auth-page">
      <header className="auth-page-header">
        <h1>零基础编程助手</h1>
        <p>登录开始你的编程学习之旅</p>
      </header>
      <main className="auth-page-main">
        <AuthForm
          mode="login"
          onSubmit={handleLogin}
          error={error}
        />
      </main>
    </div>
  );
}

export default LoginPage;