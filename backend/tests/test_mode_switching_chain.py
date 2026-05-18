# backend/tests/test_mode_switching_chain.py
"""
Tests for ModeSwitchingChain class.
"""

import pytest
from app.chains.mode_switching_chain import ModeSwitchingChain


class TestModeSwitchingChain:
    """Tests for ModeSwitchingChain class."""

    def test_init_default_mode(self):
        """Test that ModeSwitchingChain initializes with default mode 'teaching'."""
        chain = ModeSwitchingChain()
        assert chain.get_current_mode() == 'teaching'

    def test_init_custom_mode(self):
        """Test that ModeSwitchingChain can be initialized with custom mode."""
        chain = ModeSwitchingChain(mode='practical')
        assert chain.get_current_mode() == 'practical'

    def test_init_invalid_mode_raises_error(self):
        """Test that initializing with invalid mode raises ValueError."""
        with pytest.raises(ValueError, match="Invalid mode"):
            ModeSwitchingChain(mode='invalid')

    def test_switch_mode_to_practical(self):
        """Test switching mode from teaching to practical."""
        chain = ModeSwitchingChain()
        chain.switch_mode('practical')
        assert chain.get_current_mode() == 'practical'

    def test_switch_mode_to_teaching(self):
        """Test switching mode from practical to teaching."""
        chain = ModeSwitchingChain(mode='practical')
        chain.switch_mode('teaching')
        assert chain.get_current_mode() == 'teaching'

    def test_switch_mode_same_mode(self):
        """Test switching to the same mode works without error."""
        chain = ModeSwitchingChain()
        chain.switch_mode('teaching')
        assert chain.get_current_mode() == 'teaching'

    def test_switch_mode_invalid_raises_error(self):
        """Test that switching to invalid mode raises ValueError."""
        chain = ModeSwitchingChain()
        with pytest.raises(ValueError, match="Invalid mode"):
            chain.switch_mode('invalid_mode')

    def test_get_current_mode_returns_string(self):
        """Test that get_current_mode returns a string."""
        chain = ModeSwitchingChain()
        mode = chain.get_current_mode()
        assert isinstance(mode, str)
        assert mode in ['teaching', 'practical']

    def test_get_mode_config_teaching(self):
        """Test that get_mode_config returns correct config for teaching mode."""
        chain = ModeSwitchingChain()
        config = chain.get_mode_config()

        assert isinstance(config, dict)
        assert config['response_style'] == '详细解释'
        assert config['code_style'] == '逐行注释'
        assert config['learning_focus'] is True

    def test_get_mode_config_practical(self):
        """Test that get_mode_config returns correct config for practical mode."""
        chain = ModeSwitchingChain(mode='practical')
        config = chain.get_mode_config()

        assert isinstance(config, dict)
        assert config['response_style'] == '简洁快速'
        assert config['code_style'] == '完整可执行'
        assert config['learning_focus'] is False

    def test_get_mode_config_after_switch(self):
        """Test that get_mode_config updates after mode switch."""
        chain = ModeSwitchingChain()
        config_teaching = chain.get_mode_config()
        assert config_teaching['response_style'] == '详细解释'

        chain.switch_mode('practical')
        config_practical = chain.get_mode_config()
        assert config_practical['response_style'] == '简洁快速'

    def test_get_mode_prompt_teaching(self):
        """Test that get_mode_prompt returns correct prompt for teaching mode."""
        chain = ModeSwitchingChain()
        prompt = chain.get_mode_prompt('teaching')

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Should contain teaching-specific elements
        assert '详细解释' in prompt or '学习建议' in prompt or '难度标注' in prompt

    def test_get_mode_prompt_practical(self):
        """Test that get_mode_prompt returns correct prompt for practical mode."""
        chain = ModeSwitchingChain()
        prompt = chain.get_mode_prompt('practical')

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Should contain practical-specific elements
        assert '快速生成' in prompt or '简洁' in prompt or '可执行' in prompt

    def test_get_mode_prompt_invalid_mode_raises_error(self):
        """Test that get_mode_prompt with invalid mode raises ValueError."""
        chain = ModeSwitchingChain()
        with pytest.raises(ValueError, match="Invalid mode"):
            chain.get_mode_prompt('invalid')

    def test_get_mode_prompt_current_mode(self):
        """Test get_mode_prompt with no argument returns current mode prompt."""
        chain = ModeSwitchingChain()
        prompt = chain.get_mode_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Should be teaching prompt (default mode)
        assert '详细解释' in prompt or '学习建议' in prompt

    def test_build_response_strategy_basic(self):
        """Test building response strategy with basic input."""
        chain = ModeSwitchingChain()
        strategy = chain.build_response_strategy("How do I create a variable?")

        assert isinstance(strategy, dict)
        assert 'mode' in strategy
        assert 'config' in strategy
        assert 'prompt' in strategy
        assert 'input_analysis' in strategy

    def test_build_response_strategy_teaching_mode(self):
        """Test building response strategy in teaching mode."""
        chain = ModeSwitchingChain()
        strategy = chain.build_response_strategy("What is a function?")

        assert strategy['mode'] == 'teaching'
        assert strategy['config']['learning_focus'] is True
        assert isinstance(strategy['prompt'], str)
        assert isinstance(strategy['input_analysis'], dict)

    def test_build_response_strategy_practical_mode(self):
        """Test building response strategy in practical mode."""
        chain = ModeSwitchingChain(mode='practical')
        strategy = chain.build_response_strategy("Create a counter function")

        assert strategy['mode'] == 'practical'
        assert strategy['config']['learning_focus'] is False
        assert isinstance(strategy['prompt'], str)
        assert isinstance(strategy['input_analysis'], dict)

    def test_build_response_strategy_input_analysis(self):
        """Test that input_analysis contains expected fields."""
        chain = ModeSwitchingChain()
        strategy = chain.build_response_strategy("Help me understand loops")

        input_analysis = strategy['input_analysis']
        assert 'original_input' in input_analysis
        assert 'input_type' in input_analysis
        assert 'suggested_response_style' in input_analysis

    def test_build_response_strategy_detects_question(self):
        """Test that strategy detects question type input."""
        chain = ModeSwitchingChain()
        strategy = chain.build_response_strategy("What is a variable?")

        assert strategy['input_analysis']['input_type'] == 'question'

    def test_build_response_strategy_detects_code_request(self):
        """Test that strategy detects code request type input."""
        chain = ModeSwitchingChain()
        strategy = chain.build_response_strategy("Create a function to sort a list")

        assert strategy['input_analysis']['input_type'] == 'code_request'

    def test_build_response_strategy_detects_concept_inquiry(self):
        """Test that strategy detects concept inquiry type input."""
        chain = ModeSwitchingChain()
        strategy = chain.build_response_strategy("Explain what a loop is")

        assert strategy['input_analysis']['input_type'] == 'concept_inquiry'

    def test_build_response_strategy_empty_input(self):
        """Test building response strategy with empty input."""
        chain = ModeSwitchingChain()
        strategy = chain.build_response_strategy("")

        assert isinstance(strategy, dict)
        assert strategy['mode'] == 'teaching'
        assert 'input_analysis' in strategy

    def test_mode_switching_chain_singleton_behavior(self):
        """Test that multiple instances are independent."""
        chain1 = ModeSwitchingChain()
        chain2 = ModeSwitchingChain()

        chain1.switch_mode('practical')
        assert chain1.get_current_mode() == 'practical'
        assert chain2.get_current_mode() == 'teaching'

    def test_teaching_mode_prompt_contains_all_elements(self):
        """Test that teaching mode prompt contains all required elements."""
        chain = ModeSwitchingChain()
        prompt = chain.get_mode_prompt('teaching')

        # Teaching mode should include these elements
        assert '详细解释' in prompt
        assert '学习建议' in prompt
        assert '难度标注' in prompt

    def test_practical_mode_prompt_contains_all_elements(self):
        """Test that practical mode prompt contains all required elements."""
        chain = ModeSwitchingChain()
        prompt = chain.get_mode_prompt('practical')

        # Practical mode should include these elements
        assert '快速生成' in prompt or '简洁快速' in prompt
        assert '依赖安装' in prompt or '安装' in prompt or 'dependency' in prompt.lower()

    def test_mode_config_has_all_required_keys(self):
        """Test that mode config has all required keys."""
        chain = ModeSwitchingChain()

        teaching_config = chain.get_mode_config('teaching')
        assert 'response_style' in teaching_config
        assert 'code_style' in teaching_config
        assert 'learning_focus' in teaching_config

        practical_config = chain.get_mode_config('practical')
        assert 'response_style' in practical_config
        assert 'code_style' in practical_config
        assert 'learning_focus' in practical_config

    def test_get_mode_config_with_argument(self):
        """Test that get_mode_config works with explicit mode argument."""
        chain = ModeSwitchingChain()
        config = chain.get_mode_config('practical')

        assert config['response_style'] == '简洁快速'
        assert chain.get_current_mode() == 'teaching'  # Should not change current mode