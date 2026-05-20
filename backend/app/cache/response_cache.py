# backend/app/cache/response_cache.py
"""
Response cache for storing and retrieving AI responses.

Provides in-memory caching with TTL (Time-To-Live) support to reduce
duplicate API calls and improve response times.
"""

import hashlib
import time
from typing import Any, Dict, Optional


class ResponseCache:
    """
    In-memory response cache with TTL support.

    Stores responses based on user input, difficulty level, and mode.
    Supports automatic expiration and cache statistics.
    """

    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the response cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 3600 = 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def _generate_cache_key(
        self,
        user_input: str,
        difficulty: str,
        mode: str
    ) -> str:
        """
        Generate a unique cache key using MD5 hash.

        Args:
            user_input: The user's input message
            difficulty: Difficulty level (e.g., 'beginner', 'intermediate', 'advanced')
            mode: Current mode (e.g., 'teaching', 'practical')

        Returns:
            MD5 hash string as the cache key
        """
        key_string = f"{user_input}:{difficulty}:{mode}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

    def get(
        self,
        user_input: str,
        difficulty: str,
        mode: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response if it exists and hasn't expired.

        Args:
            user_input: The user's input message
            difficulty: Difficulty level
            mode: Current mode

        Returns:
            Cached response data if found and valid, None otherwise
        """
        cache_key = self._generate_cache_key(user_input, difficulty, mode)

        if cache_key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[cache_key]
        current_time = time.time()

        # Check if entry has expired
        if current_time > entry['expires_at']:
            del self._cache[cache_key]
            self._misses += 1
            return None

        self._hits += 1
        return entry['response']

    def set(
        self,
        user_input: str,
        difficulty: str,
        mode: str,
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """
        Store a response in the cache.

        Args:
            user_input: The user's input message
            difficulty: Difficulty level
            mode: Current mode
            response: The response data to cache
            ttl: Time-to-live in seconds (uses default_ttl if not provided)
        """
        cache_key = self._generate_cache_key(user_input, difficulty, mode)
        current_time = time.time()
        effective_ttl = ttl if ttl is not None else self._default_ttl

        self._cache[cache_key] = {
            'response': response,
            'created_at': current_time,
            'expires_at': current_time + effective_ttl,
            'ttl': effective_ttl
        }

    def clear_expired(self) -> int:
        """
        Remove all expired entries from the cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary containing cache statistics:
            - total_entries: Total number of cached entries
            - hits: Number of cache hits
            - misses: Number of cache misses
            - hit_rate: Cache hit rate as a percentage
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0

        return {
            'total_entries': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': round(hit_rate, 2)
        }

    def clear_all(self) -> None:
        """
        Clear all entries from the cache and reset statistics.
        """
        self._cache.clear()
        self._hits = 0
        self._misses = 0