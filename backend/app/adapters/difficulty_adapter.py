# backend/app/adapters/difficulty_adapter.py
"""
Difficulty Adapter for assessing user skill levels.

This module provides functionality to:
- Assess user difficulty level based on their interaction history
- Calculate difficulty scores from various metrics
- Retrieve user data for difficulty assessment
"""

from typing import Dict, List, Any, Literal

DifficultyLevel = Literal['beginner', 'intermediate', 'advanced']


class DifficultyAdapter:
    """
    Adapter for assessing and managing user difficulty levels.

    Analyzes user interaction history to determine appropriate
    difficulty level for content presentation.

    Attributes:
        BEGINNER_THRESHOLD: Score threshold for beginner level (< 30)
        INTERMEDIATE_THRESHOLD: Score threshold for intermediate level (30-70)
        MAX_QUESTION_COMPLEXITY_SCORE: Maximum points for question complexity (40)
        MAX_CODE_MODIFICATION_SCORE: Maximum points for code modifications (30)
        MAX_TERMINOLOGY_SCORE: Maximum points for terminology usage (20)
        MAX_CONCEPTS_SCORE: Maximum points for concepts learned (10)
    """

    # Difficulty thresholds
    BEGINNER_THRESHOLD = 30
    INTERMEDIATE_THRESHOLD = 70

    # Maximum scores for each component
    MAX_QUESTION_COMPLEXITY_SCORE = 40
    MAX_CODE_MODIFICATION_SCORE = 30
    MAX_TERMINOLOGY_SCORE = 20
    MAX_CONCEPTS_SCORE = 10

    def __init__(self):
        """Initialize the DifficultyAdapter."""
        # In production, this would connect to a database
        # Currently uses mock data for development
        pass

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get user interaction history data for difficulty assessment.

        Currently returns mock data. In production, this would
        fetch real data from a database.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing:
            - question_complexity_history: List of complexity ratings (1-10)
            - code_modification_complexity: Score for code modification depth (0-30)
            - terminology_usage_level: Level of technical term usage (0-20)
            - concepts_learned_count: Number of concepts learned (0-10)
        """
        # Return default/empty data for mock implementation
        # In production, this would query the database
        return {
            'question_complexity_history': [],
            'code_modification_complexity': 0,
            'terminology_usage_level': 0,
            'concepts_learned_count': 0
        }

    def calculate_difficulty_score(self, user_data: Dict[str, Any]) -> float:
        """
        Calculate an overall difficulty score from user data.

        Scoring breakdown:
        - question_complexity_history: 0-40 points (capped)
        - code_modification_complexity: 0-30 points
        - terminology_usage_level: 0-20 points
        - concepts_learned_count: 0-10 points

        Args:
            user_data: Dictionary containing user interaction metrics

        Returns:
            Score between 0 and 100
        """
        score = 0.0

        # 1. Question complexity history: 0-40 points
        # Calculate average complexity and multiply by 4, capped at 40
        question_history = user_data.get('question_complexity_history', [])
        if question_history:
            avg_complexity = sum(question_history) / len(question_history)
            question_score = min(avg_complexity * 4, self.MAX_QUESTION_COMPLEXITY_SCORE)
            score += question_score

        # 2. Code modification complexity: 0-30 points
        code_score = min(
            user_data.get('code_modification_complexity', 0),
            self.MAX_CODE_MODIFICATION_SCORE
        )
        score += code_score

        # 3. Terminology usage level: 0-20 points
        terminology_score = min(
            user_data.get('terminology_usage_level', 0),
            self.MAX_TERMINOLOGY_SCORE
        )
        score += terminology_score

        # 4. Concepts learned count: 0-10 points
        concepts_score = min(
            user_data.get('concepts_learned_count', 0),
            self.MAX_CONCEPTS_SCORE
        )
        score += concepts_score

        return score

    def assess_difficulty(self, user_id: str) -> DifficultyLevel:
        """
        Assess and return the difficulty level for a user.

        Level thresholds:
        - < 30: beginner
        - 30-70: intermediate
        - >= 70: advanced

        Args:
            user_id: Unique identifier for the user

        Returns:
            'beginner', 'intermediate', or 'advanced'
        """
        user_data = self.get_user_data(user_id)
        score = self.calculate_difficulty_score(user_data)

        # Check for empty/minimal data (new user)
        question_history = user_data.get('question_complexity_history', [])
        code_mod = user_data.get('code_modification_complexity', 0)
        terminology = user_data.get('terminology_usage_level', 0)
        concepts = user_data.get('concepts_learned_count', 0)

        # If no history data, default to beginner
        if not question_history and code_mod == 0 and terminology == 0 and concepts == 0:
            return 'beginner'

        # Determine level based on score
        if score < self.BEGINNER_THRESHOLD:
            return 'beginner'
        elif score < self.INTERMEDIATE_THRESHOLD:
            return 'intermediate'
        else:
            return 'advanced'