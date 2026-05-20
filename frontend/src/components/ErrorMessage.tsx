/**
 * ErrorMessage Component
 * Displays error messages with dismiss functionality
 */

import type { FC } from 'react';

interface ErrorMessageProps {
  message: string;
  onDismiss: () => void;
}

const ErrorMessage: FC<ErrorMessageProps> = ({ message, onDismiss }) => {
  return (
    <div className="error-message-container">
      <span className="error-message-icon">⚠️</span>
      <span className="error-message-text">{message}</span>
      <button
        type="button"
        className="dismiss-button"
        onClick={onDismiss}
        aria-label="Dismiss error"
      >
        ✖
      </button>
    </div>
  );
};

export default ErrorMessage;