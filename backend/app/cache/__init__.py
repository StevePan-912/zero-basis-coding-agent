# backend/app/cache/__init__.py
"""
Cache module for response caching.
"""

from app.cache.response_cache import ResponseCache

__all__ = ['ResponseCache']