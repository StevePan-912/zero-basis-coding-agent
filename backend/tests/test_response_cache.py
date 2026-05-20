# backend/tests/test_response_cache.py
"""
Tests for ResponseCache.
"""

import pytest
import time
from app.cache import ResponseCache


class TestResponseCache:
    """Tests for ResponseCache class."""

    def test_cache_set_and_get(self):
        """Test setting and getting a cache entry."""
        cache = ResponseCache()

        user_input = "What is Python?"
        difficulty = "beginner"
        mode = "teaching"
        response = {
            'response': 'Python is a programming language.',
            'difficulty': difficulty,
            'mode': mode
        }

        # Set cache
        cache.set(user_input, difficulty, mode, response)

        # Get cache
        cached_response = cache.get(user_input, difficulty, mode)

        assert cached_response is not None
        assert cached_response == response

    def test_cache_miss(self):
        """Test cache miss for non-existent entry."""
        cache = ResponseCache()

        cached_response = cache.get(
            user_input="What is Python?",
            difficulty="beginner",
            mode="teaching"
        )

        assert cached_response is None

    def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        cache = ResponseCache(default_ttl=1)  # 1 second TTL

        user_input = "What is Python?"
        difficulty = "beginner"
        mode = "teaching"
        response = {
            'response': 'Python is a programming language.',
            'difficulty': difficulty,
            'mode': mode
        }

        # Set cache with 1 second TTL
        cache.set(user_input, difficulty, mode, response)

        # Should be present immediately
        cached_response = cache.get(user_input, difficulty, mode)
        assert cached_response is not None

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired now
        cached_response = cache.get(user_input, difficulty, mode)
        assert cached_response is None

    def test_clear_expired(self):
        """Test clearing expired entries."""
        cache = ResponseCache(default_ttl=1)  # 1 second TTL

        # Set multiple entries
        cache.set("question1", "beginner", "teaching", {'response': 'answer1'})
        cache.set("question2", "intermediate", "teaching", {'response': 'answer2'})

        # Verify entries exist
        stats = cache.get_cache_stats()
        assert stats['total_entries'] == 2

        # Wait for expiration
        time.sleep(1.5)

        # Clear expired entries
        removed_count = cache.clear_expired()

        assert removed_count == 2

        # Verify cache is empty
        stats = cache.get_cache_stats()
        assert stats['total_entries'] == 0

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = ResponseCache()

        # Initial stats
        stats = cache.get_cache_stats()
        assert stats['total_entries'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['hit_rate'] == 0.0

        # Set and get an entry (should be a hit)
        cache.set("question", "beginner", "teaching", {'response': 'answer'})
        cache.get("question", "beginner", "teaching")

        stats = cache.get_cache_stats()
        assert stats['total_entries'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 0
        assert stats['hit_rate'] == 100.0

        # Try to get a non-existent entry (should be a miss)
        cache.get("nonexistent", "beginner", "teaching")

        stats = cache.get_cache_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0

    def test_cache_key_uniqueness(self):
        """Test that different inputs produce different cache keys."""
        cache = ResponseCache()

        response1 = {'response': 'answer1'}
        response2 = {'response': 'answer2'}
        response3 = {'response': 'answer3'}

        # Set entries with different parameters
        cache.set("question", "beginner", "teaching", response1)
        cache.set("question", "intermediate", "teaching", response2)
        cache.set("question", "beginner", "practical", response3)

        # Each should return its own response
        result1 = cache.get("question", "beginner", "teaching")
        result2 = cache.get("question", "intermediate", "teaching")
        result3 = cache.get("question", "beginner", "practical")

        assert result1 == response1
        assert result2 == response2
        assert result3 == response3

    def test_custom_ttl(self):
        """Test setting custom TTL for cache entries."""
        cache = ResponseCache(default_ttl=3600)  # 1 hour default

        user_input = "What is Python?"
        difficulty = "beginner"
        mode = "teaching"
        response = {'response': 'Python is a programming language.'}

        # Set with custom TTL of 1 second
        cache.set(user_input, difficulty, mode, response, ttl=1)

        # Should be present immediately
        cached_response = cache.get(user_input, difficulty, mode)
        assert cached_response is not None

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired now
        cached_response = cache.get(user_input, difficulty, mode)
        assert cached_response is None

    def test_clear_all(self):
        """Test clearing all cache entries."""
        cache = ResponseCache()

        # Set multiple entries
        cache.set("question1", "beginner", "teaching", {'response': 'answer1'})
        cache.set("question2", "intermediate", "teaching", {'response': 'answer2'})

        # Generate some hits and misses
        cache.get("question1", "beginner", "teaching")  # hit
        cache.get("nonexistent", "beginner", "teaching")  # miss

        # Verify state
        stats = cache.get_cache_stats()
        assert stats['total_entries'] == 2
        assert stats['hits'] == 1
        assert stats['misses'] == 1

        # Clear all
        cache.clear_all()

        # Verify cleared state
        stats = cache.get_cache_stats()
        assert stats['total_entries'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0

    def test_cache_update(self):
        """Test that setting same key overwrites previous entry."""
        cache = ResponseCache()

        user_input = "What is Python?"
        difficulty = "beginner"
        mode = "teaching"

        # Set initial response
        cache.set(user_input, difficulty, mode, {'response': 'answer1'})

        # Overwrite with new response
        cache.set(user_input, difficulty, mode, {'response': 'answer2'})

        # Should return the new response
        result = cache.get(user_input, difficulty, mode)
        assert result == {'response': 'answer2'}

        # Should still have only 1 entry
        stats = cache.get_cache_stats()
        assert stats['total_entries'] == 1

    def test_cache_hit_rate_calculation(self):
        """Test hit rate calculation accuracy."""
        cache = ResponseCache()

        # Set one entry
        cache.set("question", "beginner", "teaching", {'response': 'answer'})

        # Generate 3 hits
        cache.get("question", "beginner", "teaching")
        cache.get("question", "beginner", "teaching")
        cache.get("question", "beginner", "teaching")

        # Generate 1 miss
        cache.get("nonexistent", "beginner", "teaching")

        stats = cache.get_cache_stats()
        assert stats['hits'] == 3
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 75.0  # 3 out of 4 = 75%