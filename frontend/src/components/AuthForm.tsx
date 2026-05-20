/**
 * AuthForm Component
 * A generic authentication form component for login and registration
 */

import { useState, FormEvent } from 'react';
import type { LoginRequest, RegisterRequest } from '../types';

// Use function overloads to properly type the onSubmit based on mode
interface BaseAuthFormProps {
  error: string | null;
}

interface LoginAuthFormProps extends BaseAuthFormProps {
  mode: 'login';
  onSubmit: (data: LoginRequest) => Promise<void>;
}

interface RegisterAuthFormProps extends BaseAuthFormProps {
  mode: 'register';
  onSubmit: (data: RegisterRequest) => Promise<void>;
}

type AuthFormProps = LoginAuthFormProps | RegisterAuthFormProps;

function AuthForm(props: AuthFormProps) {
  const { mode, onSubmit, error } = props;

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const isRegisterMode = mode === 'register';

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormError(null);

    // Basic validation
    if (!username.trim()) {
      setFormError('请输入用户名');
      return;
    }
    if (!password.trim()) {
      setFormError('请输入密码');
      return;
    }
    if (isRegisterMode && !email.trim()) {
      setFormError('请输入邮箱');
      return;
    }
    if (isRegisterMode && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setFormError('请输入有效的邮箱地址');
      return;
    }

    setIsLoading(true);
    try {
      if (isRegisterMode) {
        // TypeScript narrows the type correctly here
        await onSubmit({ username: username.trim(), email: email.trim(), password });
      } else {
        // TypeScript narrows the type correctly here
        await onSubmit({ username: username.trim(), password });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const displayError = error || formError;

  return (
    <div className="auth-form-container">
      <h2 className="auth-form-title">
        {isRegisterMode ? '注册账号' : '登录'}
      </h2>

      <form className="auth-form" onSubmit={handleSubmit}>
        {displayError && (
          <div className="auth-form-error">
            {displayError}
          </div>
        )}

        <div className="auth-form-field">
          <label htmlFor="username">用户名</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="请输入用户名"
            disabled={isLoading}
            autoComplete="username"
          />
        </div>

        {isRegisterMode && (
          <div className="auth-form-field">
            <label htmlFor="email">邮箱</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="请输入邮箱"
              disabled={isLoading}
              autoComplete="email"
            />
          </div>
        )}

        <div className="auth-form-field">
          <label htmlFor="password">密码</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="请输入密码"
            disabled={isLoading}
            autoComplete={isRegisterMode ? 'new-password' : 'current-password'}
          />
        </div>

        <button
          type="submit"
          className="auth-form-submit"
          disabled={isLoading}
        >
          {isLoading ? '处理中...' : (isRegisterMode ? '注册' : '登录')}
        </button>
      </form>

      <div className="auth-form-switch">
        {isRegisterMode ? (
          <span>
            已有账号？<a href="/login">立即登录</a>
          </span>
        ) : (
          <span>
            还没有账号？<a href="/register">立即注册</a>
          </span>
        )}
      </div>
    </div>
  );
}

export default AuthForm;