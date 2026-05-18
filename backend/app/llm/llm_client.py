# backend/app/llm/llm_client.py
"""
LLM Client module for interacting with Claude and OpenAI APIs.
"""

from typing import Optional, List, Dict, Any
from app.config import Config


class LLMClient:
    """
    LLM Client for interacting with Claude and OpenAI APIs.

    Supports:
    - Multiple providers (claude, openai)
    - Mock mode for testing
    - System prompts
    - Conversation history
    """

    SUPPORTED_PROVIDERS = ['claude', 'openai']
    MOCK_RESPONSE = 'MOCK_RESPONSE'

    def __init__(
        self,
        provider: str = 'claude',
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        mock_mode: bool = False,
        **kwargs
    ):
        """
        Initialize LLM Client.

        Args:
            provider: LLM provider ('claude' or 'openai')
            api_key: API key (optional, will use Config if not provided)
            model: Model name (optional, uses default for provider)
            mock_mode: If True, returns mock responses without API calls
            **kwargs: Additional arguments for the LLM client
        """
        provider_lower = provider.lower()
        if provider_lower not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {self.SUPPORTED_PROVIDERS}"
            )

        self.provider = provider_lower
        self.mock_mode = mock_mode
        self.model = model
        self.kwargs = kwargs
        self._client = None

        # Set API key
        if api_key:
            self.api_key = api_key
        else:
            # Get from Config based on provider
            if self.provider == 'claude':
                self.api_key = Config.CLAUDE_API_KEY
            else:
                self.api_key = Config.OPENAI_API_KEY

        # Initialize client if not in mock mode
        if not self.mock_mode:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LangChain client."""
        if self.provider == 'claude':
            from langchain_anthropic import ChatAnthropic

            model = self.model or 'claude-3-sonnet-20240229'
            self._client = ChatAnthropic(
                model=model,
                anthropic_api_key=self.api_key,
                **self.kwargs
            )
        elif self.provider == 'openai':
            from langchain_openai import ChatOpenAI

            model = self.model or 'gpt-4-turbo-preview'
            self._client = ChatOpenAI(
                model=model,
                openai_api_key=self.api_key,
                **self.kwargs
            )

    def invoke(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """
        Invoke the LLM with a message.

        Args:
            message: User message
            system_prompt: Optional system prompt
            conversation_history: Optional list of previous messages
            **kwargs: Additional arguments for the invoke call

        Returns:
            LLM response as string
        """
        if self.mock_mode:
            return self.MOCK_RESPONSE

        # Build messages list
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({'role': 'user', 'content': message})

        # Invoke the LLM
        response = self._client.invoke(messages, **kwargs)

        # Extract content from response
        if hasattr(response, 'content'):
            return response.content
        return str(response)

    def get_client(self):
        """Get the underlying LangChain client."""
        return self._client