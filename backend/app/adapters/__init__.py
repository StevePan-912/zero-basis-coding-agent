# backend/app/adapters/__init__.py
"""
Adapters module for difficulty assessment and prompt building.

Provides:
- DifficultyAdapter: Assess user skill levels
- PromptBuilder: Build dynamic prompts based on difficulty and mode
"""

from app.adapters.difficulty_adapter import DifficultyAdapter
from app.adapters.prompt_builder import PromptBuilder

__all__ = ['DifficultyAdapter', 'PromptBuilder']