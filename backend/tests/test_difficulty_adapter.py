# backend/tests/test_difficulty_adapter.py
"""
Tests for DifficultyAdapter and PromptBuilder classes.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.adapters.difficulty_adapter import DifficultyAdapter
from app.adapters.prompt_builder import PromptBuilder


class TestDifficultyAdapter:
    """Tests for DifficultyAdapter class."""

    def test_init(self):
        """Test DifficultyAdapter initialization."""
        adapter = DifficultyAdapter()
        assert adapter is not None

    def test_get_user_data_returns_dict(self):
        """Test that get_user_data returns a dictionary."""
        adapter = DifficultyAdapter()
        user_data = adapter.get_user_data('test_user')

        assert isinstance(user_data, dict)

    def test_get_user_data_new_user_returns_empty(self):
        """Test that new user returns empty/default data."""
        adapter = DifficultyAdapter()
        user_data = adapter.get_user_data('new_user_123')

        # Should return default data for new users
        assert isinstance(user_data, dict)
        assert 'question_complexity_history' in user_data
        assert 'code_modification_complexity' in user_data
        assert 'terminology_usage_level' in user_data
        assert 'concepts_learned_count' in user_data

    def test_calculate_difficulty_score_empty_data(self):
        """Test score calculation with empty/minimal data."""
        adapter = DifficultyAdapter()
        user_data = {
            'question_complexity_history': [],
            'code_modification_complexity': 0,
            'terminology_usage_level': 0,
            'concepts_learned_count': 0
        }

        score = adapter.calculate_difficulty_score(user_data)
        assert score == 0
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_calculate_difficulty_score_beginner(self):
        """Test score calculation for beginner level."""
        adapter = DifficultyAdapter()
        user_data = {
            'question_complexity_history': [2, 3, 2],  # avg ~2.33, * 4 = ~9.3
            'code_modification_complexity': 5,          # 5 points
            'terminology_usage_level': 3,               # 3 points
            'concepts_learned_count': 2                 # 2 points
        }
        # Expected: min(9.33, 40) + 5 + 3 + 2 = ~19.33 (beginner: < 30)

        score = adapter.calculate_difficulty_score(user_data)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
        assert score < 30  # Should be beginner

    def test_calculate_difficulty_score_intermediate(self):
        """Test score calculation for intermediate level."""
        adapter = DifficultyAdapter()
        user_data = {
            'question_complexity_history': [6, 7, 5, 6],  # avg 6, * 4 = 24
            'code_modification_complexity': 20,            # 20 points
            'terminology_usage_level': 12,                 # 12 points
            'concepts_learned_count': 8                    # 8 points
        }
        # Expected: min(24, 40) + 20 + 12 + 8 = 64 (intermediate: 30-70)

        score = adapter.calculate_difficulty_score(user_data)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
        assert 30 <= score < 70  # Should be intermediate

    def test_calculate_difficulty_score_advanced(self):
        """Test score calculation for advanced level."""
        adapter = DifficultyAdapter()
        user_data = {
            'question_complexity_history': [9, 10, 8, 9, 10],  # avg ~9.2, * 4 = ~36.8
            'code_modification_complexity': 28,                  # 28 points
            'terminology_usage_level': 18,                       # 18 points
            'concepts_learned_count': 10                         # 10 points
        }
        # Expected: min(36.8, 40) + 28 + 18 + 10 = 92.8 (advanced: >= 70)

        score = adapter.calculate_difficulty_score(user_data)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
        assert score >= 70  # Should be advanced

    def test_calculate_difficulty_score_question_complexity_cap(self):
        """Test that question complexity is capped at 40 points."""
        adapter = DifficultyAdapter()
        user_data = {
            'question_complexity_history': [15, 20, 25],  # avg 20, * 4 = 80, capped at 40
            'code_modification_complexity': 0,
            'terminology_usage_level': 0,
            'concepts_learned_count': 0
        }

        score = adapter.calculate_difficulty_score(user_data)
        # Question complexity should contribute max 40 points
        assert score <= 40

    def test_assess_difficulty_new_user_returns_beginner(self):
        """Test that new user is assessed as beginner."""
        adapter = DifficultyAdapter()
        difficulty = adapter.assess_difficulty('new_user_no_history')

        assert difficulty == 'beginner'

    def test_assess_difficulty_beginner_threshold(self):
        """Test difficulty assessment for beginner threshold."""
        adapter = DifficultyAdapter()

        # Mock user data that gives score < 30
        with patch.object(adapter, 'get_user_data') as mock_get_data:
            mock_get_data.return_value = {
                'question_complexity_history': [2, 3],
                'code_modification_complexity': 5,
                'terminology_usage_level': 3,
                'concepts_learned_count': 2
            }

            difficulty = adapter.assess_difficulty('test_user')
            assert difficulty == 'beginner'

    def test_assess_difficulty_intermediate_threshold(self):
        """Test difficulty assessment for intermediate threshold."""
        adapter = DifficultyAdapter()

        # Mock user data that gives score between 30-70
        with patch.object(adapter, 'get_user_data') as mock_get_data:
            mock_get_data.return_value = {
                'question_complexity_history': [6, 7, 5, 6],
                'code_modification_complexity': 20,
                'terminology_usage_level': 12,
                'concepts_learned_count': 8
            }

            difficulty = adapter.assess_difficulty('test_user')
            assert difficulty == 'intermediate'

    def test_assess_difficulty_advanced_threshold(self):
        """Test difficulty assessment for advanced threshold."""
        adapter = DifficultyAdapter()

        # Mock user data that gives score >= 70
        with patch.object(adapter, 'get_user_data') as mock_get_data:
            mock_get_data.return_value = {
                'question_complexity_history': [9, 10, 8, 9, 10],
                'code_modification_complexity': 28,
                'terminology_usage_level': 18,
                'concepts_learned_count': 10
            }

            difficulty = adapter.assess_difficulty('test_user')
            assert difficulty == 'advanced'

    def test_scoring_components_sum_correctly(self):
        """Test that all scoring components contribute correctly."""
        adapter = DifficultyAdapter()

        # Test each component individually
        user_data_1 = {
            'question_complexity_history': [10],  # 10 * 4 = 40, capped at 40
            'code_modification_complexity': 0,
            'terminology_usage_level': 0,
            'concepts_learned_count': 0
        }
        score_1 = adapter.calculate_difficulty_score(user_data_1)
        assert score_1 == 40  # Only question complexity (capped)

        user_data_2 = {
            'question_complexity_history': [],
            'code_modification_complexity': 30,  # Max 30
            'terminology_usage_level': 0,
            'concepts_learned_count': 0
        }
        score_2 = adapter.calculate_difficulty_score(user_data_2)
        assert score_2 == 30  # Only code modification

        user_data_3 = {
            'question_complexity_history': [],
            'code_modification_complexity': 0,
            'terminology_usage_level': 20,  # Max 20
            'concepts_learned_count': 0
        }
        score_3 = adapter.calculate_difficulty_score(user_data_3)
        assert score_3 == 20  # Only terminology

        user_data_4 = {
            'question_complexity_history': [],
            'code_modification_complexity': 0,
            'terminology_usage_level': 0,
            'concepts_learned_count': 10  # Max 10
        }
        score_4 = adapter.calculate_difficulty_score(user_data_4)
        assert score_4 == 10  # Only concepts learned


class TestPromptBuilder:
    """Tests for PromptBuilder class."""

    def test_init(self):
        """Test PromptBuilder initialization."""
        builder = PromptBuilder()
        assert builder is not None

    def test_build_prompt_basic(self):
        """Test basic prompt building."""
        builder = PromptBuilder()
        base_prompt = "Explain what a variable is."
        result = builder.build_prompt(base_prompt, difficulty='beginner', mode='teaching')

        assert isinstance(result, str)
        assert len(result) > 0
        assert base_prompt in result

    def test_build_prompt_beginner_teaching(self):
        """Test building prompt for beginner in teaching mode."""
        builder = PromptBuilder()
        base_prompt = "What is a loop?"
        result = builder.build_prompt(base_prompt, difficulty='beginner', mode='teaching')

        assert isinstance(result, str)
        # Should contain beginner-friendly instructions
        assert 'beginner' in result.lower() or 'simple' in result.lower() or 'analogy' in result.lower()

    def test_build_prompt_intermediate_teaching(self):
        """Test building prompt for intermediate in teaching mode."""
        builder = PromptBuilder()
        base_prompt = "What is a loop?"
        result = builder.build_prompt(base_prompt, difficulty='intermediate', mode='teaching')

        assert isinstance(result, str)
        # Should contain intermediate-level instructions
        assert 'intermediate' in result.lower() or 'foundation' in result.lower()

    def test_build_prompt_advanced_teaching(self):
        """Test building prompt for advanced in teaching mode."""
        builder = PromptBuilder()
        base_prompt = "What is a loop?"
        result = builder.build_prompt(base_prompt, difficulty='advanced', mode='teaching')

        assert isinstance(result, str)
        # Should contain advanced-level instructions
        assert 'advanced' in result.lower() or 'professional' in result.lower() or 'depth' in result.lower()

    def test_build_prompt_beginner_practical(self):
        """Test building prompt for beginner in practical mode."""
        builder = PromptBuilder()
        base_prompt = "Create a counter."
        result = builder.build_prompt(base_prompt, difficulty='beginner', mode='practical')

        assert isinstance(result, str)
        # Should contain practical beginner instructions
        assert 'code' in result.lower() or 'comment' in result.lower() or 'runnable' in result.lower()

    def test_build_prompt_intermediate_practical(self):
        """Test building prompt for intermediate in practical mode."""
        builder = PromptBuilder()
        base_prompt = "Create a counter."
        result = builder.build_prompt(base_prompt, difficulty='intermediate', mode='practical')

        assert isinstance(result, str)
        # Should contain practical intermediate instructions

    def test_build_prompt_advanced_practical(self):
        """Test building prompt for advanced in practical mode."""
        builder = PromptBuilder()
        base_prompt = "Create a counter."
        result = builder.build_prompt(base_prompt, difficulty='advanced', mode='practical')

        assert isinstance(result, str)
        # Should contain practical advanced instructions

    def test_add_difficulty_instructions_beginner(self):
        """Test adding difficulty instructions for beginner."""
        builder = PromptBuilder()
        instructions = builder._add_difficulty_instructions('beginner')

        assert isinstance(instructions, str)
        assert len(instructions) > 0
        # Should contain beginner-specific guidance
        assert 'simple' in instructions.lower() or 'beginner' in instructions.lower()

    def test_add_difficulty_instructions_intermediate(self):
        """Test adding difficulty instructions for intermediate."""
        builder = PromptBuilder()
        instructions = builder._add_difficulty_instructions('intermediate')

        assert isinstance(instructions, str)
        assert len(instructions) > 0

    def test_add_difficulty_instructions_advanced(self):
        """Test adding difficulty instructions for advanced."""
        builder = PromptBuilder()
        instructions = builder._add_difficulty_instructions('advanced')

        assert isinstance(instructions, str)
        assert len(instructions) > 0

    def test_add_mode_instructions_teaching(self):
        """Test adding mode instructions for teaching."""
        builder = PromptBuilder()
        instructions = builder._add_mode_instructions('teaching')

        assert isinstance(instructions, str)
        assert len(instructions) > 0
        # Should contain teaching-specific guidance
        assert 'teach' in instructions.lower() or 'learn' in instructions.lower() or 'tutor' in instructions.lower()

    def test_add_mode_instructions_practical(self):
        """Test adding mode instructions for practical."""
        builder = PromptBuilder()
        instructions = builder._add_mode_instructions('practical')

        assert isinstance(instructions, str)
        assert len(instructions) > 0
        # Should contain practical/code-specific guidance
        assert 'code' in instructions.lower() or 'solution' in instructions.lower() or 'practical' in instructions.lower()

    def test_build_concept_prompt(self):
        """Test building concept explanation prompt."""
        builder = PromptBuilder()
        concept = "variable"

        result = builder.build_concept_prompt(concept, difficulty='beginner')

        assert isinstance(result, str)
        assert len(result) > 0
        assert 'variable' in result.lower()

    def test_build_concept_prompt_with_difficulty(self):
        """Test building concept prompt respects difficulty level."""
        builder = PromptBuilder()

        beginner_result = builder.build_concept_prompt('loop', difficulty='beginner')
        advanced_result = builder.build_concept_prompt('loop', difficulty='advanced')

        # Both should mention the concept
        assert 'loop' in beginner_result.lower()
        assert 'loop' in advanced_result.lower()

        # They should differ in style/complexity
        assert beginner_result != advanced_result

    def test_build_code_prompt(self):
        """Test building code generation prompt."""
        builder = PromptBuilder()
        task_description = "Create a function that adds two numbers"

        result = builder.build_code_prompt(task_description, difficulty='beginner')

        assert isinstance(result, str)
        assert len(result) > 0
        assert 'function' in result.lower() or 'code' in result.lower()

    def test_build_code_prompt_with_difficulty(self):
        """Test building code prompt respects difficulty level."""
        builder = PromptBuilder()

        beginner_result = builder.build_code_prompt('sort a list', difficulty='beginner')
        advanced_result = builder.build_code_prompt('sort a list', difficulty='advanced')

        # Both should mention the task
        assert 'sort' in beginner_result.lower()
        assert 'sort' in advanced_result.lower()

        # They should differ in style/complexity
        assert beginner_result != advanced_result

    def test_build_code_prompt_includes_practical_instructions(self):
        """Test that code prompt includes practical mode instructions."""
        builder = PromptBuilder()
        result = builder.build_code_prompt('create a loop', difficulty='intermediate')

        # Should include code-specific instructions
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_prompt_invalid_difficulty_raises_error(self):
        """Test that invalid difficulty raises ValueError."""
        builder = PromptBuilder()

        with pytest.raises(ValueError, match="Unsupported difficulty"):
            builder.build_prompt("Test prompt", difficulty='invalid', mode='teaching')

    def test_build_prompt_invalid_mode_raises_error(self):
        """Test that invalid mode raises ValueError."""
        builder = PromptBuilder()

        with pytest.raises(ValueError, match="Unsupported mode"):
            builder.build_prompt("Test prompt", difficulty='beginner', mode='invalid')

    def test_build_concept_prompt_invalid_difficulty_raises_error(self):
        """Test that build_concept_prompt with invalid difficulty raises error."""
        builder = PromptBuilder()

        with pytest.raises(ValueError, match="Unsupported difficulty"):
            builder.build_concept_prompt('variable', difficulty='invalid')

    def test_build_code_prompt_invalid_difficulty_raises_error(self):
        """Test that build_code_prompt with invalid difficulty raises error."""
        builder = PromptBuilder()

        with pytest.raises(ValueError, match="Unsupported difficulty"):
            builder.build_code_prompt('create a function', difficulty='invalid')