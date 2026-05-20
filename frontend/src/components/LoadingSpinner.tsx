/**
 * LoadingSpinner Component
 * Displays a loading spinner with optional message
 */

import type { FC } from 'react';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: FC<LoadingSpinnerProps> = ({ message = '加载中...' }) => {
  return (
    <div className="loading-spinner-container">
      <div className="spinner" />
      <p className="loading-spinner-message">{message}</p>
    </div>
  );
};

export default LoadingSpinner;