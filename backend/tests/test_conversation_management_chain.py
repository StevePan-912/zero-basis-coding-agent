# backend/tests/test_conversation_management_chain.py
"""
Tests for ConversationManagementChain class.
"""

import pytest
from datetime import datetime
from app.chains.conversation_management_chain import ConversationManagementChain


class TestConversationManagementChain:
    """Tests for ConversationManagementChain class."""

    def test_init_with_user_id(self):
        """Test that ConversationManagementChain initializes with user_id."""
        chain = ConversationManagementChain(user_id='user123')
        assert chain.user_id == 'user123'
        assert chain.session_id is not None
        assert isinstance(chain.session_id, str)
        assert len(chain.session_id) > 0

    def test_init_generates_unique_session_ids(self):
        """Test that each instance generates a unique session_id."""
        chain1 = ConversationManagementChain(user_id='user1')
        chain2 = ConversationManagementChain(user_id='user2')
        assert chain1.session_id != chain2.session_id

    def test_add_message_user(self):
        """Test adding a user message."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Hello, world!')

        history = chain.get_conversation_history()
        assert len(history) == 1
        assert history[0]['role'] == 'user'
        assert history[0]['content'] == 'Hello, world!'
        assert 'timestamp' in history[0]

    def test_add_message_assistant(self):
        """Test adding an assistant message."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('assistant', 'Hi there!')

        history = chain.get_conversation_history()
        assert len(history) == 1
        assert history[0]['role'] == 'assistant'
        assert history[0]['content'] == 'Hi there!'

    def test_add_message_multiple(self):
        """Test adding multiple messages."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Message 1')
        chain.add_message('assistant', 'Message 2')
        chain.add_message('user', 'Message 3')

        history = chain.get_conversation_history()
        assert len(history) == 3
        assert history[0]['content'] == 'Message 1'
        assert history[1]['content'] == 'Message 2'
        assert history[2]['content'] == 'Message 3'

    def test_add_message_invalid_role_raises_error(self):
        """Test that adding a message with invalid role raises ValueError."""
        chain = ConversationManagementChain(user_id='user123')
        with pytest.raises(ValueError, match="Invalid role"):
            chain.add_message('system', 'Invalid message')

    def test_add_message_with_invalid_role_valueerror(self):
        """Test that invalid role raises ValueError."""
        chain = ConversationManagementChain(user_id='user123')
        with pytest.raises(ValueError):
            chain.add_message('invalid_role', 'test content')

    def test_get_conversation_history_empty(self):
        """Test getting conversation history when empty."""
        chain = ConversationManagementChain(user_id='user123')
        history = chain.get_conversation_history()
        assert isinstance(history, list)
        assert len(history) == 0

    def test_get_conversation_history_returns_copy(self):
        """Test that get_conversation_history returns a copy, not the original."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Message')

        history1 = chain.get_conversation_history()
        history2 = chain.get_conversation_history()

        # Modify one copy
        history1.append({'role': 'fake', 'content': 'fake', 'timestamp': 'fake'})

        # Other should be unchanged
        assert len(history2) == 1
        assert len(chain.get_conversation_history()) == 1

    def test_get_last_n_messages(self):
        """Test getting last N messages."""
        chain = ConversationManagementChain(user_id='user123')
        for i in range(5):
            chain.add_message('user', f'Message {i}')

        last_3 = chain.get_last_n_messages(3)
        assert len(last_3) == 3
        assert last_3[0]['content'] == 'Message 2'
        assert last_3[1]['content'] == 'Message 3'
        assert last_3[2]['content'] == 'Message 4'

    def test_get_last_n_messages_more_than_total(self):
        """Test getting last N messages when N > total messages."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Message 1')
        chain.add_message('user', 'Message 2')

        last_5 = chain.get_last_n_messages(5)
        assert len(last_5) == 2

    def test_get_last_n_messages_zero(self):
        """Test getting last 0 messages."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Message 1')

        last_0 = chain.get_last_n_messages(0)
        assert len(last_0) == 0

    def test_get_last_n_messages_empty_history(self):
        """Test getting last N messages when history is empty."""
        chain = ConversationManagementChain(user_id='user123')
        last_3 = chain.get_last_n_messages(3)
        assert len(last_3) == 0

    def test_clear_history(self):
        """Test clearing conversation history."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Message 1')
        chain.add_message('assistant', 'Message 2')

        assert len(chain.get_conversation_history()) == 2

        chain.clear_history()
        assert len(chain.get_conversation_history()) == 0

    def test_clear_history_empty(self):
        """Test clearing history when already empty."""
        chain = ConversationManagementChain(user_id='user123')
        chain.clear_history()  # Should not raise error
        assert len(chain.get_conversation_history()) == 0

    def test_message_timestamp_format(self):
        """Test that message timestamp is in ISO format."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Test message')

        history = chain.get_conversation_history()
        timestamp = history[0]['timestamp']

        # Should be able to parse as ISO format
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    def test_message_structure(self):
        """Test that message has correct structure."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Test content')

        history = chain.get_conversation_history()
        message = history[0]

        assert 'role' in message
        assert 'content' in message
        assert 'timestamp' in message
        assert len(message.keys()) == 3

    def test_get_context_window_within_limit(self):
        """Test getting context window when all messages are within token limit."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Short message')
        chain.add_message('assistant', 'Short response')

        context = chain.get_context_window(max_tokens=1000)
        assert len(context) == 2

    def test_get_context_window_exceeds_limit(self):
        """Test getting context window when messages exceed token limit."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Message 1')
        chain.add_message('assistant', 'Response 1')
        chain.add_message('user', 'Message 2')
        chain.add_message('assistant', 'Response 2')

        # Use very small token limit
        context = chain.get_context_window(max_tokens=5)
        # Should return fewer messages
        assert len(context) < 4

    def test_get_context_window_empty_history(self):
        """Test getting context window when history is empty."""
        chain = ConversationManagementChain(user_id='user123')
        context = chain.get_context_window(max_tokens=100)
        assert len(context) == 0

    def test_save_to_database_raises_not_implemented(self):
        """Test that save_to_database raises NotImplementedError."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Test')

        with pytest.raises(NotImplementedError):
            chain.save_to_database()

    def test_load_from_database_raises_not_implemented(self):
        """Test that load_from_database raises NotImplementedError."""
        chain = ConversationManagementChain(user_id='user123')

        with pytest.raises(NotImplementedError):
            chain.load_from_database()

    def test_message_order_preserved(self):
        """Test that message order is preserved."""
        chain = ConversationManagementChain(user_id='user123')
        messages = ['First', 'Second', 'Third', 'Fourth']

        for msg in messages:
            chain.add_message('user', msg)

        history = chain.get_conversation_history()
        for i, msg in enumerate(messages):
            assert history[i]['content'] == msg

    def test_conversation_independence(self):
        """Test that different conversation instances are independent."""
        chain1 = ConversationManagementChain(user_id='user1')
        chain2 = ConversationManagementChain(user_id='user2')

        chain1.add_message('user', 'Chain 1 message')
        chain2.add_message('user', 'Chain 2 message')

        assert len(chain1.get_conversation_history()) == 1
        assert len(chain2.get_conversation_history()) == 1
        assert chain1.get_conversation_history()[0]['content'] == 'Chain 1 message'
        assert chain2.get_conversation_history()[0]['content'] == 'Chain 2 message'

    def test_get_last_n_messages_negative_raises_error(self):
        """Test that get_last_n_messages with negative N raises ValueError."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', 'Message')

        with pytest.raises(ValueError, match="must be non-negative"):
            chain.get_last_n_messages(-1)

    def test_add_message_empty_content(self):
        """Test adding a message with empty content."""
        chain = ConversationManagementChain(user_id='user123')
        chain.add_message('user', '')

        history = chain.get_conversation_history()
        assert len(history) == 1
        assert history[0]['content'] == ''

    def test_get_context_window_approximate_token_count(self):
        """Test that get_context_window uses approximate token counting."""
        chain = ConversationManagementChain(user_id='user123')

        # Add messages with known approximate token counts
        # "Hello world" is approximately 2-3 tokens
        chain.add_message('user', 'Hello world')
        chain.add_message('assistant', 'Hello world')

        # Should include both messages with generous limit
        context = chain.get_context_window(max_tokens=100)
        assert len(context) == 2

    def test_session_id_persists_after_operations(self):
        """Test that session_id remains constant after operations."""
        chain = ConversationManagementChain(user_id='user123')
        original_session_id = chain.session_id

        chain.add_message('user', 'Message 1')
        chain.add_message('assistant', 'Response 1')
        chain.clear_history()
        chain.add_message('user', 'Message 2')

        assert chain.session_id == original_session_id

    def test_user_id_persists_after_operations(self):
        """Test that user_id remains constant after operations."""
        chain = ConversationManagementChain(user_id='test_user')
        original_user_id = chain.user_id

        chain.add_message('user', 'Message')
        chain.clear_history()

        assert chain.user_id == original_user_id