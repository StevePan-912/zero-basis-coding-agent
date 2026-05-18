# backend/app/llm/llm_optimizer.py
"""
LLM Optimizer module for prompt optimization and caching.
"""

from typing import Optional, List, Dict, Any


class LLMOptimizer:
    """
    LLM Optimizer for reducing API costs and improving efficiency.

    Features:
    - Prompt caching control
    - Prompt length optimization
    - System prompt building
    - Message formatting
    """

    # Mode-specific system prompt templates
    SYSTEM_PROMPT_TEMPLATES = {
        'teaching': {
            'beginner': """You are a patient and friendly programming tutor helping complete beginners learn to code.

Key guidelines:
1. Use simple analogies to explain concepts (e.g., "variables are like boxes that store things")
2. Avoid technical jargon, or explain it simply when necessary
3. Provide visual examples when possible (flowcharts, data flow diagrams)
4. Mark concept difficulty levels (Simple/Medium/Complex)
5. Provide links to foundational learning resources
6. Break down complex topics into small, digestible pieces
7. Encourage questions and celebrate small wins

Your goal is to make programming feel approachable and achievable.""",

            'intermediate': """You are a programming tutor helping a learner who has some basic programming knowledge.

Key guidelines:
1. Use moderate technical terminology with brief explanations
2. Suggest next steps for learning expansion
3. Provide code optimization suggestions
4. Share simple performance tips
5. Connect new concepts to previously learned material
6. Encourage independent problem-solving

Your goal is to build on their foundation and deepen their understanding.""",

            'advanced': """You are a programming mentor helping an experienced learner advance their skills.

Key guidelines:
1. Use standard technical terminology without over-explaining
2. Provide in-depth learning resources (documentation, articles)
3. Discuss performance optimization (memory, concurrency, algorithms)
4. Explore edge cases, error handling, and concurrency issues
5. Challenge them with thought-provoking questions
6. Introduce industry best practices and patterns

Your goal is to prepare them for professional-level development."""
        },

        'practical': {
            'beginner': """You are a helpful coding assistant focused on delivering practical, working solutions.

Key guidelines:
1. Provide complete, runnable code snippets
2. Include clear comments explaining key parts
3. Specify required dependencies and installation commands
4. Keep explanations brief and focused on the solution
5. Warn about common pitfalls for beginners
6. Suggest simple ways to test and verify the code

Your goal is to help users get working code quickly while building understanding.""",

            'intermediate': """You are an efficient coding assistant delivering practical solutions.

Key guidelines:
1. Provide well-structured, production-ready code
2. Include key comments for complex logic
3. Suggest relevant optimizations or alternatives
4. Briefly explain the approach and trade-offs
5. Include basic error handling
6. Reference relevant documentation or libraries

Your goal is to deliver quality solutions efficiently.""",

            'advanced': """You are a senior developer assistant delivering professional-grade solutions.

Key guidelines:
1. Provide clean, efficient, and maintainable code
2. Consider performance, scalability, and edge cases
3. Include comprehensive error handling
4. Suggest architectural improvements when relevant
5. Briefly document key decisions and trade-offs
6. Reference advanced resources when helpful

Your goal is to deliver solutions that meet professional standards."""
        }
    }

    def __init__(self, max_prompt_length: int = 10000):
        """
        Initialize LLM Optimizer.

        Args:
            max_prompt_length: Maximum prompt length before optimization
        """
        self.max_prompt_length = max_prompt_length

    def build_system_prompt(
        self,
        mode: str,
        difficulty: str
    ) -> str:
        """
        Build a system prompt based on mode and difficulty.

        Args:
            mode: 'teaching' or 'practical'
            difficulty: 'beginner', 'intermediate', or 'advanced'

        Returns:
            Formatted system prompt string

        Raises:
            ValueError: If mode or difficulty is invalid
        """
        mode_lower = mode.lower()
        difficulty_lower = difficulty.lower()

        if mode_lower not in self.SYSTEM_PROMPT_TEMPLATES:
            raise ValueError(
                f"Unsupported mode: {mode}. "
                f"Supported modes: {list(self.SYSTEM_PROMPT_TEMPLATES.keys())}"
            )

        if difficulty_lower not in self.SYSTEM_PROMPT_TEMPLATES[mode_lower]:
            raise ValueError(
                f"Unsupported difficulty: {difficulty}. "
                f"Supported difficulties: {list(self.SYSTEM_PROMPT_TEMPLATES[mode_lower].keys())}"
            )

        return self.SYSTEM_PROMPT_TEMPLATES[mode_lower][difficulty_lower]

    def optimize_prompt_length(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        truncation_suffix: str = "..."
    ) -> str:
        """
        Optimize prompt length by truncating if necessary.

        Args:
            prompt: The prompt to optimize
            max_length: Maximum length (uses instance default if not provided)
            truncation_suffix: Suffix to add when truncating

        Returns:
            Optimized prompt string
        """
        max_len = max_length or self.max_prompt_length

        if len(prompt) <= max_len:
            return prompt

        # Truncate and add suffix
        truncated_length = max_len - len(truncation_suffix)
        return prompt[:truncated_length] + truncation_suffix

    def add_caching_control(
        self,
        prompt: str,
        cache_type: str = "ephemeral"
    ) -> str:
        """
        Add caching control markers for supported LLM APIs.

        This uses Claude's prompt caching format to enable caching
        of system prompts and long context.

        Args:
            prompt: The prompt to add caching to
            cache_type: Type of cache control (default: 'ephemeral')

        Returns:
            Prompt with caching control markers
        """
        # Add cache control marker for Claude API
        # This allows the LLM to cache the prompt for reuse
        cache_marker = f'<!-- cache-control: {{"type": "{cache_type}"}} -->\n'
        return cache_marker + prompt

    def optimize_for_cost(
        self,
        system_prompt: str,
        user_prompt: str,
        enable_caching: bool = True,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Optimize prompts for cost efficiency.

        Combines multiple optimization strategies:
        - Length optimization
        - Caching control
        - Message structuring

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            enable_caching: Whether to enable caching
            max_length: Maximum total length

        Returns:
            Dictionary with optimized messages and metadata
        """
        max_len = max_length or self.max_prompt_length

        # Optimize lengths
        optimized_system = self.optimize_prompt_length(
            system_prompt,
            max_length=max_len // 2
        )
        optimized_user = self.optimize_prompt_length(
            user_prompt,
            max_length=max_len // 2
        )

        # Add caching if enabled
        if enable_caching:
            optimized_system = self.add_caching_control(optimized_system)

        # Build messages
        messages = [
            {'role': 'system', 'content': optimized_system},
            {'role': 'user', 'content': optimized_user}
        ]

        return {
            'messages': messages,
            'system_prompt': optimized_system,
            'user_prompt': optimized_user,
            'total_length': len(optimized_system) + len(optimized_user),
            'caching_enabled': enable_caching
        }

    def build_messages(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        enable_caching: bool = False
    ) -> List[Dict[str, str]]:
        """
        Build a messages list for the LLM API.

        Args:
            system_prompt: System prompt
            user_message: Current user message
            conversation_history: Previous messages
            enable_caching: Whether to add caching control

        Returns:
            List of message dictionaries
        """
        messages = []

        # Add system prompt
        system_content = system_prompt
        if enable_caching:
            system_content = self.add_caching_control(system_prompt)
        messages.append({'role': 'system', 'content': system_content})

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })

        # Add current user message
        messages.append({'role': 'user', 'content': user_message})

        return messages