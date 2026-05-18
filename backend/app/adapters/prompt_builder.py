# backend/app/adapters/prompt_builder.py
"""
Prompt Builder for dynamically constructing LLM prompts.

This module provides functionality to:
- Build prompts based on difficulty level and mode
- Add difficulty-specific instructions
- Add mode-specific instructions
- Create concept explanation prompts
- Create code generation prompts
"""

from typing import Literal

DifficultyLevel = Literal['beginner', 'intermediate', 'advanced']
ModeType = Literal['teaching', 'practical']


class PromptBuilder:
    """
    Builder for dynamically constructing prompts based on difficulty and mode.

    Creates customized prompts that adapt to the user's skill level
    and preferred interaction mode.

    Attributes:
        DIFFICULTY_INSTRUCTIONS: Templates for each difficulty level
        MODE_INSTRUCTIONS: Templates for each interaction mode
    """

    DIFFICULTY_INSTRUCTIONS = {
        'beginner': """
## Beginner-Friendly Guidelines:
- Use simple analogies and real-world examples (e.g., "variables are like labeled boxes")
- Avoid technical jargon; explain terms simply when necessary
- Break down complex concepts into small, digestible steps
- Provide visual descriptions when possible
- Encourage questions and celebrate progress
- Focus on "what" and "how" before "why"
- Include links to foundational resources
""",
        'intermediate': """
## Intermediate-Level Guidelines:
- Use moderate technical terminology with brief explanations
- Connect new concepts to foundational knowledge
- Suggest next steps for deeper learning
- Provide optimization tips and best practices
- Encourage independent problem-solving
- Balance theory with practical examples
""",
        'advanced': """
## Advanced-Level Guidelines:
- Use standard technical terminology without over-explaining
- Provide in-depth resources (documentation, articles, research)
- Discuss performance, scalability, and edge cases
- Introduce industry patterns and best practices
- Challenge with thought-provoking questions
- Focus on trade-offs and architectural decisions
"""
    }

    MODE_INSTRUCTIONS = {
        'teaching': """
## Teaching Mode Instructions:
Your role is to be a patient and effective tutor. Your goal is to help the learner
understand concepts deeply, not just provide quick answers.

Teaching approach:
- Guide the learner to discover answers through questions
- Provide structured explanations with clear progression
- Check understanding with follow-up questions
- Adapt explanations based on learner's responses
- Build confidence while ensuring comprehension
""",
        'practical': """
## Practical Mode Instructions:
Your role is to help the user accomplish their specific coding task efficiently.
Focus on delivering working solutions with clear explanations.

Practical approach:
- Provide complete, runnable code examples
- Include necessary dependencies and setup instructions
- Explain key parts of the code clearly
- Warn about common pitfalls and errors
- Suggest testing and verification methods
- Keep explanations focused and actionable
"""
    }

    CONCEPT_PROMPT_TEMPLATES = {
        'beginner': """Please explain the concept of "{concept}" in simple terms.

{difficulty_instructions}

Use analogies and everyday examples to make it easy to understand.
Avoid technical jargon unless absolutely necessary, and explain it simply if used.""",

        'intermediate': """Please explain the concept of "{concept}" with appropriate depth.

{difficulty_instructions}

Connect this concept to practical applications and related concepts.
Provide examples that show both basic and more advanced usage.""",

        'advanced': """Please provide a comprehensive explanation of "{concept}".

{difficulty_instructions}

Include:
- Technical details and implementation considerations
- Performance implications and edge cases
- Real-world applications and best practices
- References to further learning resources"""
    }

    CODE_PROMPT_TEMPLATES = {
        'beginner': """Please help me with the following coding task:

{task}

{difficulty_instructions}
{mode_instructions}

Please provide:
1. A complete, simple solution with clear comments
2. Step-by-step explanation of how the code works
3. Simple instructions for running and testing the code
4. Common beginner mistakes to avoid""",

        'intermediate': """Please help me with the following coding task:

{task}

{difficulty_instructions}
{mode_instructions}

Please provide:
1. A well-structured solution with key comments
2. Brief explanation of the approach and any trade-offs
3. Suggestions for potential optimizations or alternatives
4. Error handling considerations""",

        'advanced': """Please help me with the following coding task:

{task}

{difficulty_instructions}
{mode_instructions}

Please provide:
1. A production-ready, efficient solution
2. Key architectural decisions and trade-offs
3. Performance considerations and edge case handling
4. References to relevant documentation or patterns"""
    }

    def __init__(self):
        """Initialize the PromptBuilder."""
        pass

    def _add_difficulty_instructions(self, difficulty: DifficultyLevel) -> str:
        """
        Get difficulty-specific instructions.

        Args:
            difficulty: 'beginner', 'intermediate', or 'advanced'

        Returns:
            Difficulty-specific instruction string

        Raises:
            ValueError: If difficulty is not valid
        """
        if difficulty not in self.DIFFICULTY_INSTRUCTIONS:
            raise ValueError(
                f"Unsupported difficulty: {difficulty}. "
                f"Supported difficulties: {list(self.DIFFICULTY_INSTRUCTIONS.keys())}"
            )

        return self.DIFFICULTY_INSTRUCTIONS[difficulty]

    def _add_mode_instructions(self, mode: ModeType) -> str:
        """
        Get mode-specific instructions.

        Args:
            mode: 'teaching' or 'practical'

        Returns:
            Mode-specific instruction string

        Raises:
            ValueError: If mode is not valid
        """
        if mode not in self.MODE_INSTRUCTIONS:
            raise ValueError(
                f"Unsupported mode: {mode}. "
                f"Supported modes: {list(self.MODE_INSTRUCTIONS.keys())}"
            )

        return self.MODE_INSTRUCTIONS[mode]

    def build_prompt(
        self,
        base_prompt: str,
        difficulty: DifficultyLevel,
        mode: ModeType
    ) -> str:
        """
        Build a complete prompt with difficulty and mode instructions.

        Args:
            base_prompt: The base user prompt/question
            difficulty: 'beginner', 'intermediate', or 'advanced'
            mode: 'teaching' or 'practical'

        Returns:
            Complete prompt with all instructions

        Raises:
            ValueError: If difficulty or mode is invalid
        """
        # Validate inputs
        if difficulty not in self.DIFFICULTY_INSTRUCTIONS:
            raise ValueError(
                f"Unsupported difficulty: {difficulty}. "
                f"Supported difficulties: {list(self.DIFFICULTY_INSTRUCTIONS.keys())}"
            )

        if mode not in self.MODE_INSTRUCTIONS:
            raise ValueError(
                f"Unsupported mode: {mode}. "
                f"Supported modes: {list(self.MODE_INSTRUCTIONS.keys())}"
            )

        difficulty_instructions = self._add_difficulty_instructions(difficulty)
        mode_instructions = self._add_mode_instructions(mode)

        # Construct the full prompt
        full_prompt = f"""{mode_instructions}

{difficulty_instructions}

## User Request:
{base_prompt}
"""
        return full_prompt

    def build_concept_prompt(
        self,
        concept: str,
        difficulty: DifficultyLevel
    ) -> str:
        """
        Build a prompt for explaining a concept.

        Args:
            concept: The concept to explain
            difficulty: 'beginner', 'intermediate', or 'advanced'

        Returns:
            Concept explanation prompt

        Raises:
            ValueError: If difficulty is invalid
        """
        if difficulty not in self.CONCEPT_PROMPT_TEMPLATES:
            raise ValueError(
                f"Unsupported difficulty: {difficulty}. "
                f"Supported difficulties: {list(self.CONCEPT_PROMPT_TEMPLATES.keys())}"
            )

        template = self.CONCEPT_PROMPT_TEMPLATES[difficulty]
        difficulty_instructions = self._add_difficulty_instructions(difficulty)

        return template.format(
            concept=concept,
            difficulty_instructions=difficulty_instructions.strip()
        )

    def build_code_prompt(
        self,
        task: str,
        difficulty: DifficultyLevel
    ) -> str:
        """
        Build a prompt for generating code.

        Args:
            task: Description of the coding task
            difficulty: 'beginner', 'intermediate', or 'advanced'

        Returns:
            Code generation prompt

        Raises:
            ValueError: If difficulty is invalid
        """
        if difficulty not in self.CODE_PROMPT_TEMPLATES:
            raise ValueError(
                f"Unsupported difficulty: {difficulty}. "
                f"Supported difficulties: {list(self.CODE_PROMPT_TEMPLATES.keys())}"
            )

        template = self.CODE_PROMPT_TEMPLATES[difficulty]
        difficulty_instructions = self._add_difficulty_instructions(difficulty)
        mode_instructions = self._add_mode_instructions('practical')

        return template.format(
            task=task,
            difficulty_instructions=difficulty_instructions.strip(),
            mode_instructions=mode_instructions.strip()
        )