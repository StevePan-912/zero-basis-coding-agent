# backend/app/chains/conversation_management_chain.py
"""
ConversationManagementChain - Manages conversation history and context.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any


class ConversationManagementChain:
    """
    Manages conversation history for a user session.

    Provides methods to add, retrieve, and manage messages within
    a conversation context window.
    """

    VALID_ROLES = {'user', 'assistant'}

    def __init__(self, user_id: str):
        """
        Initialize ConversationManagementChain with user_id.

        Args:
            user_id: Unique identifier for the user.

        Raises:
            ValueError: If user_id is empty or None.
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string")

        self._user_id = user_id
        self._session_id = str(uuid.uuid4())
        self._messages: List[Dict[str, str]] = []

    @property
    def user_id(self) -> str:
        """Get the user ID."""
        return self._user_id

    @property
    def session_id(self) -> str:
        """Get the session ID."""
        return self._session_id

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: Role of the message sender ('user' or 'assistant').
            content: Content of the message.

        Raises:
            ValueError: If role is not 'user' or 'assistant'.
        """
        if role not in self.VALID_ROLES:
            raise ValueError(
                f"Invalid role '{role}'. Must be one of: {self.VALID_ROLES}"
            )

        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self._messages.append(message)

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Return all messages in the conversation history.

        Returns:
            List of message dictionaries, each containing 'role', 'content',
            and 'timestamp' keys.
        """
        return self._messages.copy()

    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """
        Return the last N messages from the conversation history.

        Args:
            n: Number of messages to retrieve. Must be non-negative.

        Returns:
            List of the last N message dictionaries.

        Raises:
            ValueError: If n is negative.
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")

        if n == 0:
            return []

        return self._messages[-n:].copy() if self._messages else []

    def clear_history(self) -> None:
        """Clear all messages from the conversation history."""
        self._messages.clear()

    def get_context_window(self, max_tokens: int = 4000) -> List[Dict[str, str]]:
        """
        Return messages within the specified token limit.

        Uses approximate token counting: ~4 characters per token on average.

        Args:
            max_tokens: Maximum number of tokens allowed. Defaults to 4000.

        Returns:
            List of message dictionaries that fit within the token limit,
            starting from the most recent and working backwards.
        """
        if not self._messages:
            return []

        result = []
        total_tokens = 0

        # Iterate backwards through messages
        for message in reversed(self._messages):
            # Approximate token count: ~4 characters per token
            # Also account for role overhead
            message_tokens = len(message['content']) // 4 + 5  # +5 for role/overhead

            if total_tokens + message_tokens > max_tokens:
                break

            result.insert(0, message)
            total_tokens += message_tokens

        return result

    def save_to_database(self) -> None:
        """
        Save conversation to database.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError(
            "save_to_database is not yet implemented. "
            "This will be implemented in a future update."
        )

    def load_from_database(self) -> None:
        """
        Load conversation from database.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError(
            "load_from_database is not yet implemented. "
            "This will be implemented in a future update."
        )