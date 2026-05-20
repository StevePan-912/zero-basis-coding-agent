# backend/app/cost/cost_controller.py
"""
Cost Controller for API usage management.

Provides rate limiting and usage tracking for users with different tiers.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class UserUsage:
    """Data class to track user API usage."""
    user_id: str
    tier: str = 'free'
    daily_calls: int = 0
    total_calls: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    last_call: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'user_id': self.user_id,
            'tier': self.tier,
            'daily_calls': self.daily_calls,
            'total_calls': self.total_calls,
            'last_reset': self.last_reset.isoformat() if self.last_reset else None,
            'last_call': self.last_call.isoformat() if self.last_call else None
        }


class CostController:
    """
    Controller for managing API usage costs and limits.

    Features:
    - Daily API call limits per tier (free: 50, paid: 500)
    - Automatic daily reset
    - Usage statistics tracking
    - Tier upgrade capability
    """

    DEFAULT_LIMITS = {
        'free': 50,
        'paid': 500
    }

    RESET_INTERVAL_HOURS = 24

    def __init__(self, limits: Optional[Dict[str, int]] = None):
        """
        Initialize the CostController.

        Args:
            limits: Optional custom limits per tier. Defaults to {'free': 50, 'paid': 500}
        """
        self.limits = limits if limits is not None else self.DEFAULT_LIMITS.copy()
        self._user_api_usage: Dict[str, UserUsage] = {}

    def get_user_usage(self, user_id: str) -> Dict[str, Any]:
        """
        Get usage information for a user.

        Args:
            user_id: The user's unique identifier

        Returns:
            Dictionary containing daily_calls, total_calls, tier, and limits
        """
        # Check if user exists, create if not
        if user_id not in self._user_api_usage:
            self._user_api_usage[user_id] = UserUsage(user_id=user_id)

        usage = self._user_api_usage[user_id]

        # Check for daily reset
        self._check_daily_reset(usage)

        return {
            'daily_calls': usage.daily_calls,
            'total_calls': usage.total_calls,
            'tier': usage.tier,
            'daily_limit': self.limits.get(usage.tier, self.limits['free']),
            'remaining': max(0, self.limits.get(usage.tier, self.limits['free']) - usage.daily_calls)
        }

    def check_limit(self, user_id: str) -> Dict[str, Any]:
        """
        Check if a user is within their API call limit.

        Args:
            user_id: The user's unique identifier

        Returns:
            Dictionary with:
                - allowed: bool indicating if the call is allowed
                - remaining: int of remaining calls for today
                - message: str explaining the status
        """
        # Ensure user exists
        if user_id not in self._user_api_usage:
            self._user_api_usage[user_id] = UserUsage(user_id=user_id)

        usage = self._user_api_usage[user_id]

        # Check for daily reset
        self._check_daily_reset(usage)

        limit = self.limits.get(usage.tier, self.limits['free'])
        remaining = limit - usage.daily_calls

        if usage.daily_calls >= limit:
            return {
                'allowed': False,
                'remaining': 0,
                'message': f"Daily API limit ({limit} calls) exceeded for {usage.tier} tier. "
                          f"Limit resets in {self._get_time_until_reset(usage)}."
            }

        return {
            'allowed': True,
            'remaining': remaining,
            'message': f"{remaining} API calls remaining today for {usage.tier} tier."
        }

    def record_api_call(self, user_id: str) -> Dict[str, Any]:
        """
        Record an API call for a user.

        Args:
            user_id: The user's unique identifier

        Returns:
            Dictionary with updated usage stats
        """
        # Ensure user exists
        if user_id not in self._user_api_usage:
            self._user_api_usage[user_id] = UserUsage(user_id=user_id)

        usage = self._user_api_usage[user_id]

        # Check for daily reset before recording
        self._check_daily_reset(usage)

        # Increment counters
        usage.daily_calls += 1
        usage.total_calls += 1
        usage.last_call = datetime.now()

        return {
            'daily_calls': usage.daily_calls,
            'total_calls': usage.total_calls,
            'tier': usage.tier,
            'remaining': max(0, self.limits.get(usage.tier, self.limits['free']) - usage.daily_calls)
        }

    def upgrade_tier(self, user_id: str, tier: str) -> Dict[str, Any]:
        """
        Upgrade a user's tier.

        Args:
            user_id: The user's unique identifier
            tier: The new tier ('free' or 'paid')

        Returns:
            Dictionary with the result of the upgrade

        Raises:
            ValueError: If tier is invalid
        """
        if tier not in self.limits:
            raise ValueError(f"Invalid tier: {tier}. Valid tiers: {list(self.limits.keys())}")

        # Ensure user exists
        if user_id not in self._user_api_usage:
            self._user_api_usage[user_id] = UserUsage(user_id=user_id)

        usage = self._user_api_usage[user_id]
        old_tier = usage.tier
        usage.tier = tier

        return {
            'success': True,
            'user_id': user_id,
            'old_tier': old_tier,
            'new_tier': tier,
            'new_limit': self.limits[tier],
            'message': f"User upgraded from {old_tier} to {tier} tier."
        }

    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed usage statistics for a user.

        Args:
            user_id: The user's unique identifier

        Returns:
            Dictionary with comprehensive usage statistics
        """
        # Ensure user exists
        if user_id not in self._user_api_usage:
            self._user_api_usage[user_id] = UserUsage(user_id=user_id)

        usage = self._user_api_usage[user_id]

        # Check for daily reset
        self._check_daily_reset(usage)

        limit = self.limits.get(usage.tier, self.limits['free'])
        time_until_reset = self._get_time_until_reset(usage)

        return {
            'user_id': user_id,
            'tier': usage.tier,
            'daily': {
                'calls': usage.daily_calls,
                'limit': limit,
                'remaining': max(0, limit - usage.daily_calls),
                'used_percentage': round((usage.daily_calls / limit) * 100, 2) if limit > 0 else 0
            },
            'total': {
                'calls': usage.total_calls
            },
            'timestamps': {
                'last_reset': usage.last_reset.isoformat() if usage.last_reset else None,
                'last_call': usage.last_call.isoformat() if usage.last_call else None,
                'time_until_reset': time_until_reset
            }
        }

    def _check_daily_reset(self, usage: UserUsage) -> bool:
        """
        Check if the daily counter should be reset and reset if needed.

        Args:
            usage: UserUsage object to check

        Returns:
            True if reset occurred, False otherwise
        """
        if usage.last_reset is None:
            usage.last_reset = datetime.now()
            return False

        now = datetime.now()
        time_since_reset = now - usage.last_reset

        if time_since_reset >= timedelta(hours=self.RESET_INTERVAL_HOURS):
            usage.daily_calls = 0
            usage.last_reset = now
            return True

        return False

    def _get_time_until_reset(self, usage: UserUsage) -> str:
        """
        Get a human-readable string of time until daily reset.

        Args:
            usage: UserUsage object to check

        Returns:
            String describing time until reset
        """
        if usage.last_reset is None:
            return "Unknown"

        next_reset = usage.last_reset + timedelta(hours=self.RESET_INTERVAL_HOURS)
        now = datetime.now()

        if next_reset <= now:
            return "Reset pending"

        time_diff = next_reset - now
        hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def get_all_users_stats(self) -> Dict[str, Any]:
        """
        Get aggregate statistics across all users.

        Returns:
            Dictionary with aggregate statistics
        """
        total_users = len(self._user_api_usage)
        free_users = sum(1 for u in self._user_api_usage.values() if u.tier == 'free')
        paid_users = sum(1 for u in self._user_api_usage.values() if u.tier == 'paid')
        total_calls_today = sum(u.daily_calls for u in self._user_api_usage.values())
        total_calls_all_time = sum(u.total_calls for u in self._user_api_usage.values())

        return {
            'total_users': total_users,
            'users_by_tier': {
                'free': free_users,
                'paid': paid_users
            },
            'calls': {
                'today': total_calls_today,
                'all_time': total_calls_all_time
            }
        }