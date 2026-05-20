/**
 * Register Page
 * Handles user registration with AuthForm component
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import authService from '../services/authService';
import type { RegisterRequest } from '../types';

function RegisterPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (data: RegisterRequest) => {
    setError(null);
    try {
      await authService.register(data);
      // Registration successful, navigate to login page
      navigate('/login', { state: { message: '注册成功，请登录' } });
    } catch (err) {
      // Handle error
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('注册失败，请稍后重试');
      }
    }
  };

  return (
    <div className="auth-page">
      <header className="auth-page-header">
        <h1>ZerGO Coding Agent</h1>
        <p>创建账号，开启编程学习之旅</p>
      </header>
      <main className="auth-page-main">
        <AuthForm
          mode="register"
          onSubmit={handleRegister}
          error={error}
        />
      </main>
    </div>
  );
}

export default RegisterPage;