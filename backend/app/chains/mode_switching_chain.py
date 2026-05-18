# backend/app/chains/mode_switching_chain.py
"""
ModeSwitchingChain - Manages teaching/practical mode switching.
"""

from typing import Dict, Optional, Any


class ModeSwitchingChain:
    """
    Manages mode switching between 'teaching' and 'practical' modes.

    Teaching mode: Detailed explanations, learning-focused, step-by-step guidance
    Practical mode: Concise responses, code-focused, quick solutions
    """

    VALID_MODES = {'teaching', 'practical'}

    MODE_CONFIGS: Dict[str, Dict[str, Any]] = {
        'teaching': {
            'response_style': '详细解释',
            'code_style': '逐行注释',
            'learning_focus': True,
        },
        'practical': {
            'response_style': '简洁快速',
            'code_style': '完整可执行',
            'learning_focus': False,
        }
    }

    MODE_PROMPTS: Dict[str, str] = {
        'teaching': """【教学模式响应指南】

1. 详细解释：对每个概念和步骤进行详细说明，使用通俗易懂的语言
2. 学习建议：提供学习路径建议，帮助用户循序渐进掌握知识
3. 难度标注：标注概念的难度级别（入门/进阶/高级）
4. 类比说明：使用生活中的类比帮助理解抽象概念
5. 可视化辅助：用图表、示意图等方式辅助说明复杂概念
6. 代码注释：代码示例需要逐行注释，解释每一行的作用
7. 错误预警：提前指出初学者可能遇到的问题和常见错误
8. 扩展阅读：提供相关的学习资源和延伸内容

请以引导者的角色，帮助用户建立扎实的基础知识。""",

        'practical': """【实战模式响应指南】

1. 快速生成：直接给出可运行的代码和解决方案
2. 简化解释：只解释关键步骤，避免冗余说明
3. 依赖安装：提供必要的依赖安装命令
4. 错误处理：代码中包含必要的错误处理逻辑
5. 完整可执行：确保代码可以直接复制运行
6. 性能提示：标注性能相关的注意事项
7. 最佳实践：使用业界标准做法

请以实用者的角色，提供高效、直接的解决方案。"""
    }

    def __init__(self, mode: str = 'teaching'):
        """
        Initialize ModeSwitchingChain with the specified mode.

        Args:
            mode: Initial mode ('teaching' or 'practical'). Defaults to 'teaching'.

        Raises:
            ValueError: If mode is not valid.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {self.VALID_MODES}")
        self._current_mode = mode

    def switch_mode(self, mode: str) -> None:
        """
        Switch to a different mode.

        Args:
            mode: Target mode ('teaching' or 'practical').

        Raises:
            ValueError: If mode is not valid.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {self.VALID_MODES}")
        self._current_mode = mode

    def get_current_mode(self) -> str:
        """
        Get the current mode.

        Returns:
            Current mode string ('teaching' or 'practical').
        """
        return self._current_mode

    def get_mode_config(self, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the configuration for the specified mode or current mode.

        Args:
            mode: Mode to get config for. If None, uses current mode.

        Returns:
            Dictionary containing mode configuration:
            - response_style: Response style description
            - code_style: Code style description
            - learning_focus: Whether to focus on learning

        Raises:
            ValueError: If mode is not valid.
        """
        target_mode = mode if mode is not None else self._current_mode

        if target_mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{target_mode}'. Must be one of: {self.VALID_MODES}")

        return self.MODE_CONFIGS[target_mode].copy()

    def get_mode_prompt(self, mode: Optional[str] = None) -> str:
        """
        Get the mode-specific prompt text.

        Args:
            mode: Mode to get prompt for. If None, uses current mode.

        Returns:
            Mode-specific prompt text.

        Raises:
            ValueError: If mode is not valid.
        """
        target_mode = mode if mode is not None else self._current_mode

        if target_mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{target_mode}'. Must be one of: {self.VALID_MODES}")

        return self.MODE_PROMPTS[target_mode]

    def _detect_input_type(self, user_input: str) -> str:
        """
        Detect the type of user input.

        Args:
            user_input: User's input string.

        Returns:
            Input type: 'question', 'code_request', or 'concept_inquiry'.
        """
        if not user_input or not user_input.strip():
            return 'unknown'

        input_lower = user_input.lower().strip()

        # Detect code request patterns
        code_patterns = [
            'create', 'make', 'build', 'write', 'implement',
            '生成', '创建', '编写', '实现', '写一个', '帮我写',
            'function', 'class', 'code', 'script', 'program',
            '函数', '类', '代码', '脚本', '程序'
        ]

        for pattern in code_patterns:
            if pattern in input_lower:
                return 'code_request'

        # Detect question patterns
        question_patterns = [
            '?', '？', 'what', 'how', 'why', 'when', 'where',
            'what is', 'how to', 'why does',
            '是什么', '怎么', '为什么', '如何', '什么是'
        ]

        for pattern in question_patterns:
            if pattern in input_lower:
                # Check if it's more of a concept inquiry
                if any(word in input_lower for word in ['explain', 'understand', '概念', '解释', '理解']):
                    return 'concept_inquiry'
                return 'question'

        # Check for concept inquiry keywords
        concept_patterns = [
            'explain', 'understand', 'learn', 'tell me about',
            '解释', '理解', '学习', '了解', '介绍一下'
        ]

        for pattern in concept_patterns:
            if pattern in input_lower:
                return 'concept_inquiry'

        # Default to question
        return 'question'

    def _suggest_response_style(self, input_type: str) -> str:
        """
        Suggest response style based on input type.

        Args:
            input_type: Type of input ('question', 'code_request', 'concept_inquiry').

        Returns:
            Suggested response style.
        """
        style_map = {
            'question': 'explanatory',
            'code_request': 'implementation',
            'concept_inquiry': 'educational',
            'unknown': 'general'
        }
        return style_map.get(input_type, 'general')

    def build_response_strategy(self, user_input: str) -> Dict[str, Any]:
        """
        Build a response strategy based on user input and current mode.

        Args:
            user_input: User's input string.

        Returns:
            Dictionary containing:
            - mode: Current mode
            - config: Current mode configuration
            - prompt: Mode-specific prompt
            - input_analysis: Analysis of user input
        """
        input_type = self._detect_input_type(user_input)
        suggested_style = self._suggest_response_style(input_type)

        return {
            'mode': self._current_mode,
            'config': self.get_mode_config(),
            'prompt': self.get_mode_prompt(),
            'input_analysis': {
                'original_input': user_input,
                'input_type': input_type,
                'suggested_response_style': suggested_style,
            }
        }