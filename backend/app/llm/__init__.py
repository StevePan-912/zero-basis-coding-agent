# backend/app/llm/__init__.py
"""
LLM module for interacting with language models.

Provides:
- LLMClient: Client for Claude and OpenAI APIs
- LLMOptimizer: Prompt optimization and caching utilities
"""

from app.llm.llm_client import LLMClient
from app.llm.llm_optimizer import LLMOptimizer

__all__ = ['LLMClient', 'LLMOptimizer']