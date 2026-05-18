# backend/tests/test_llm_client.py
"""
Tests for LLMClient and LLMOptimizer classes.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.llm import LLMClient, LLMOptimizer


class TestLLMClient:
    """Tests for LLMClient class."""

    def test_init_with_claude_provider(self):
        """Test LLMClient initialization with Claude provider."""
        client = LLMClient(provider='claude', api_key='test-key')
        assert client.provider == 'claude'
        assert client.api_key == 'test-key'

    def test_init_with_openai_provider(self):
        """Test LLMClient initialization with OpenAI provider."""
        client = LLMClient(provider='openai', api_key='test-key')
        assert client.provider == 'openai'
        assert client.api_key == 'test-key'

    def test_init_with_invalid_provider_raises_error(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            LLMClient(provider='invalid', api_key='test-key')

    def test_init_with_mock_mode(self):
        """Test LLMClient initialization in mock mode."""
        client = LLMClient(provider='claude', api_key='test-key', mock_mode=True)
        assert client.mock_mode is True

    def test_invoke_with_claude(self):
        """Test invoke method with Claude provider."""
        with patch('langchain_anthropic.ChatAnthropic') as mock_claude:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(content='Test response')
            mock_claude.return_value = mock_instance

            client = LLMClient(provider='claude', api_key='test-key')
            response = client.invoke('Hello')

            assert response is not None
            mock_instance.invoke.assert_called_once()

    def test_invoke_with_openai(self):
        """Test invoke method with OpenAI provider."""
        with patch('langchain_openai.ChatOpenAI') as mock_openai:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(content='Test response')
            mock_openai.return_value = mock_instance

            client = LLMClient(provider='openai', api_key='test-key')
            response = client.invoke('Hello')

            assert response is not None
            mock_instance.invoke.assert_called_once()

    def test_invoke_in_mock_mode(self):
        """Test invoke method in mock mode returns mock response."""
        client = LLMClient(provider='claude', api_key='test-key', mock_mode=True)
        response = client.invoke('Hello')

        assert response is not None
        assert 'mock' in response.lower() or response == 'MOCK_RESPONSE'

    def test_invoke_with_system_prompt(self):
        """Test invoke method with system prompt."""
        with patch('langchain_anthropic.ChatAnthropic') as mock_claude:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(content='Test response')
            mock_claude.return_value = mock_instance

            client = LLMClient(provider='claude', api_key='test-key')
            response = client.invoke('Hello', system_prompt='You are a helpful assistant.')

            assert response is not None
            # Verify that the call included system prompt handling
            call_args = mock_instance.invoke.call_args
            assert call_args is not None

    def test_invoke_with_conversation_history(self):
        """Test invoke method with conversation history."""
        with patch('langchain_anthropic.ChatAnthropic') as mock_claude:
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(content='Test response')
            mock_claude.return_value = mock_instance

            client = LLMClient(provider='claude', api_key='test-key')
            history = [
                {'role': 'user', 'content': 'Hi'},
                {'role': 'assistant', 'content': 'Hello!'}
            ]
            response = client.invoke('How are you?', conversation_history=history)

            assert response is not None


class TestLLMOptimizer:
    """Tests for LLMOptimizer class."""

    def test_init(self):
        """Test LLMOptimizer initialization."""
        optimizer = LLMOptimizer()
        assert optimizer is not None

    def test_build_system_prompt_teaching_mode(self):
        """Test building system prompt for teaching mode."""
        optimizer = LLMOptimizer()
        system_prompt = optimizer.build_system_prompt(
            mode='teaching',
            difficulty='beginner'
        )

        assert system_prompt is not None
        assert len(system_prompt) > 0
        # Teaching mode uses "tutor" terminology
        assert 'tutor' in system_prompt.lower() or 'teach' in system_prompt.lower()
        assert 'beginner' in system_prompt.lower() or 'begin' in system_prompt.lower()

    def test_build_system_prompt_practical_mode(self):
        """Test building system prompt for practical mode."""
        optimizer = LLMOptimizer()
        system_prompt = optimizer.build_system_prompt(
            mode='practical',
            difficulty='intermediate'
        )

        assert system_prompt is not None
        assert len(system_prompt) > 0
        # Practical mode should have different content than teaching
        assert 'practical' in system_prompt.lower() or 'code' in system_prompt.lower()

    def test_build_system_prompt_invalid_mode_raises_error(self):
        """Test that invalid mode raises ValueError."""
        optimizer = LLMOptimizer()
        with pytest.raises(ValueError, match="Unsupported mode"):
            optimizer.build_system_prompt(mode='invalid', difficulty='beginner')

    def test_optimize_prompt_length(self):
        """Test prompt length optimization."""
        optimizer = LLMOptimizer()
        long_prompt = "This is a test. " * 100  # Create a long prompt
        optimized = optimizer.optimize_prompt_length(long_prompt, max_length=500)

        assert len(optimized) <= 500

    def test_optimize_prompt_length_no_change_needed(self):
        """Test that short prompts are not modified."""
        optimizer = LLMOptimizer()
        short_prompt = "This is a short prompt."
        optimized = optimizer.optimize_prompt_length(short_prompt, max_length=500)

        assert optimized == short_prompt

    def test_add_caching_control(self):
        """Test adding caching control to prompts."""
        optimizer = LLMOptimizer()
        prompt = "Hello, this is a test prompt."
        cached_prompt = optimizer.add_caching_control(prompt)

        assert 'cache' in cached_prompt.lower() or 'ephemeral' in cached_prompt.lower()
        assert prompt in cached_prompt

    def test_optimize_for_cost(self):
        """Test cost optimization combines multiple optimizations."""
        optimizer = LLMOptimizer()
        system_prompt = "You are a helpful assistant."
        user_prompt = "Please help me with " + "x" * 1000  # Long prompt

        optimized = optimizer.optimize_for_cost(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            enable_caching=True
        )

        assert optimized is not None
        assert 'system_prompt' in optimized or 'messages' in optimized or isinstance(optimized, str)

    def test_build_messages_with_history(self):
        """Test building messages list with conversation history."""
        optimizer = LLMOptimizer()
        system_prompt = "You are a helpful assistant."
        user_message = "Hello"
        history = [
            {'role': 'user', 'content': 'Hi'},
            {'role': 'assistant', 'content': 'Hello!'}
        ]

        messages = optimizer.build_messages(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=history
        )

        assert messages is not None
        assert isinstance(messages, list)
        # Should contain system, history messages, and current user message
        assert len(messages) >= 3

    def test_build_messages_without_history(self):
        """Test building messages list without conversation history."""
        optimizer = LLMOptimizer()
        system_prompt = "You are a helpful assistant."
        user_message = "Hello"

        messages = optimizer.build_messages(
            system_prompt=system_prompt,
            user_message=user_message
        )

        assert messages is not None
        assert isinstance(messages, list)
        assert len(messages) == 2  # System + user message