# backend/tests/test_cost_controller.py
"""
Tests for Cost Controller.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.cost import CostController, UserUsage


class TestCostControllerInit:
    """Tests for CostController initialization."""

    def test_init_default_limits(self):
        """Test initialization with default limits."""
        controller = CostController()
        assert controller.limits == {'free': 50, 'paid': 500}

    def test_init_custom_limits(self):
        """Test initialization with custom limits."""
        custom_limits = {'free': 100, 'paid': 1000, 'enterprise': 5000}
        controller = CostController(limits=custom_limits)
        assert controller.limits == custom_limits


class TestGetUserUsage:
    """Tests for get_user_usage method."""

    def test_get_user_usage_new_user(self):
        """Test getting usage for a new user."""
        controller = CostController()
        usage = controller.get_user_usage('user1')

        assert usage['daily_calls'] == 0
        assert usage['total_calls'] == 0
        assert usage['tier'] == 'free'
        assert usage['daily_limit'] == 50
        assert usage['remaining'] == 50

    def test_get_user_usage_existing_user(self):
        """Test getting usage for an existing user."""
        controller = CostController()
        controller.record_api_call('user1')
        controller.record_api_call('user1')

        usage = controller.get_user_usage('user1')

        assert usage['daily_calls'] == 2
        assert usage['total_calls'] == 2
        assert usage['tier'] == 'free'
        assert usage['remaining'] == 48


class TestCheckLimit:
    """Tests for check_limit method."""

    def test_check_limit_allowed(self):
        """Test that limit check passes when under limit."""
        controller = CostController()
        result = controller.check_limit('user1')

        assert result['allowed'] is True
        assert result['remaining'] == 50
        assert 'remaining' in result['message'].lower()

    def test_check_limit_exceeded(self):
        """Test that limit check fails when over limit."""
        controller = CostController(limits={'free': 2, 'paid': 10})

        # Make 2 calls to reach limit
        controller.record_api_call('user1')
        controller.record_api_call('user1')

        # This check should show limit exceeded
        result = controller.check_limit('user1')

        assert result['allowed'] is False
        assert result['remaining'] == 0
        assert 'exceeded' in result['message'].lower()

    def test_check_limit_paid_tier(self):
        """Test limit check for paid tier user."""
        controller = CostController()
        controller.upgrade_tier('user1', 'paid')

        result = controller.check_limit('user1')

        assert result['allowed'] is True
        assert result['remaining'] == 500

    def test_check_limit_near_limit(self):
        """Test limit check when close to limit."""
        controller = CostController(limits={'free': 10, 'paid': 100})

        # Make 9 calls
        for _ in range(9):
            controller.record_api_call('user1')

        result = controller.check_limit('user1')

        assert result['allowed'] is True
        assert result['remaining'] == 1


class TestRecordApiCall:
    """Tests for record_api_call method."""

    def test_record_api_call_first_call(self):
        """Test recording the first API call."""
        controller = CostController()
        result = controller.record_api_call('user1')

        assert result['daily_calls'] == 1
        assert result['total_calls'] == 1
        assert result['tier'] == 'free'
        assert result['remaining'] == 49

    def test_record_api_call_multiple_calls(self):
        """Test recording multiple API calls."""
        controller = CostController()

        for i in range(5):
            result = controller.record_api_call('user1')
            assert result['daily_calls'] == i + 1

        assert result['total_calls'] == 5
        assert result['remaining'] == 45

    def test_record_api_call_updates_last_call(self):
        """Test that record_api_call updates last_call timestamp."""
        controller = CostController()
        controller.record_api_call('user1')

        stats = controller.get_usage_stats('user1')
        assert stats['timestamps']['last_call'] is not None


class TestUpgradeTier:
    """Tests for upgrade_tier method."""

    def test_upgrade_tier_free_to_paid(self):
        """Test upgrading from free to paid tier."""
        controller = CostController()
        result = controller.upgrade_tier('user1', 'paid')

        assert result['success'] is True
        assert result['old_tier'] == 'free'
        assert result['new_tier'] == 'paid'
        assert result['new_limit'] == 500

    def test_upgrade_tier_invalid_tier(self):
        """Test upgrading to an invalid tier."""
        controller = CostController()

        with pytest.raises(ValueError) as excinfo:
            controller.upgrade_tier('user1', 'premium')

        assert 'Invalid tier' in str(excinfo.value)

    def test_upgrade_tier_preserves_usage(self):
        """Test that upgrading tier preserves usage counts."""
        controller = CostController()

        # Make some calls as free user
        controller.record_api_call('user1')
        controller.record_api_call('user1')

        # Upgrade to paid
        controller.upgrade_tier('user1', 'paid')

        usage = controller.get_user_usage('user1')
        assert usage['daily_calls'] == 2
        assert usage['total_calls'] == 2
        assert usage['tier'] == 'paid'

    def test_upgrade_tier_new_user(self):
        """Test upgrading tier for a new user creates them automatically."""
        controller = CostController()
        result = controller.upgrade_tier('new_user', 'paid')

        assert result['success'] is True
        assert result['user_id'] == 'new_user'


class TestGetUsageStats:
    """Tests for get_usage_stats method."""

    def test_get_usage_stats_new_user(self):
        """Test getting stats for a new user."""
        controller = CostController()
        stats = controller.get_usage_stats('user1')

        assert stats['user_id'] == 'user1'
        assert stats['tier'] == 'free'
        assert stats['daily']['calls'] == 0
        assert stats['daily']['limit'] == 50
        assert stats['daily']['remaining'] == 50
        assert stats['daily']['used_percentage'] == 0
        assert stats['total']['calls'] == 0

    def test_get_usage_stats_with_usage(self):
        """Test getting stats for a user with usage."""
        controller = CostController()

        for _ in range(25):
            controller.record_api_call('user1')

        stats = controller.get_usage_stats('user1')

        assert stats['daily']['calls'] == 25
        assert stats['daily']['limit'] == 50
        assert stats['daily']['remaining'] == 25
        assert stats['daily']['used_percentage'] == 50.0

    def test_get_usage_stats_timestamps(self):
        """Test that stats include timestamps."""
        controller = CostController()
        controller.record_api_call('user1')

        stats = controller.get_usage_stats('user1')

        assert stats['timestamps']['last_reset'] is not None
        assert stats['timestamps']['last_call'] is not None
        assert stats['timestamps']['time_until_reset'] is not None


class TestDailyReset:
    """Tests for daily reset functionality."""

    def test_daily_reset_resets_counter(self):
        """Test that daily reset resets the daily counter."""
        controller = CostController()

        # Make some calls
        for _ in range(10):
            controller.record_api_call('user1')

        # Verify we have 10 calls
        usage = controller.get_user_usage('user1')
        assert usage['daily_calls'] == 10

        # Simulate time passing (more than 24 hours)
        with patch('app.cost.cost_controller.datetime') as mock_datetime:
            # Set current time to 25 hours later
            base_time = datetime.now()
            mock_datetime.now.return_value = base_time + timedelta(hours=25)

            # Get usage which should trigger reset
            usage = controller.get_user_usage('user1')
            assert usage['daily_calls'] == 0
            assert usage['remaining'] == 50

    def test_daily_reset_preserves_total(self):
        """Test that daily reset preserves total calls."""
        controller = CostController()

        # Make some calls
        for _ in range(10):
            controller.record_api_call('user1')

        # Simulate time passing
        with patch('app.cost.cost_controller.datetime') as mock_datetime:
            base_time = datetime.now()
            mock_datetime.now.return_value = base_time + timedelta(hours=25)

            # Trigger reset
            usage = controller.get_user_usage('user1')

            assert usage['daily_calls'] == 0
            assert usage['total_calls'] == 10  # Total should be preserved

    def test_daily_reset_updates_reset_time(self):
        """Test that daily reset updates the last_reset timestamp."""
        controller = CostController()
        controller.record_api_call('user1')

        original_stats = controller.get_usage_stats('user1')
        original_reset = original_stats['timestamps']['last_reset']

        # Simulate time passing
        with patch('app.cost.cost_controller.datetime') as mock_datetime:
            base_time = datetime.now()
            mock_datetime.now.return_value = base_time + timedelta(hours=25)

            controller.record_api_call('user1')
            new_stats = controller.get_usage_stats('user1')
            new_reset = new_stats['timestamps']['last_reset']

            # The reset time should have been updated
            assert new_reset != original_reset


class TestGetAllUsersStats:
    """Tests for aggregate statistics."""

    def test_get_all_users_stats_empty(self):
        """Test aggregate stats with no users."""
        controller = CostController()
        stats = controller.get_all_users_stats()

        assert stats['total_users'] == 0
        assert stats['users_by_tier']['free'] == 0
        assert stats['users_by_tier']['paid'] == 0
        assert stats['calls']['today'] == 0
        assert stats['calls']['all_time'] == 0

    def test_get_all_users_stats_multiple_users(self):
        """Test aggregate stats with multiple users."""
        controller = CostController()

        # Create some users with different tiers and usage
        controller.record_api_call('user1')
        controller.record_api_call('user1')
        controller.record_api_call('user2')
        controller.upgrade_tier('user3', 'paid')
        controller.record_api_call('user3')

        stats = controller.get_all_users_stats()

        assert stats['total_users'] == 3
        assert stats['users_by_tier']['free'] == 2
        assert stats['users_by_tier']['paid'] == 1
        assert stats['calls']['today'] == 4
        assert stats['calls']['all_time'] == 4

    def test_get_all_users_stats_after_reset(self):
        """Test aggregate stats after daily reset."""
        controller = CostController()

        # Make some calls
        controller.record_api_call('user1')
        controller.record_api_call('user2')

        # Simulate reset for one user
        with patch('app.cost.cost_controller.datetime') as mock_datetime:
            base_time = datetime.now()
            mock_datetime.now.return_value = base_time + timedelta(hours=25)

            # Trigger reset for user1
            controller.record_api_call('user1')

            stats = controller.get_all_users_stats()

            # user1 should have been reset (0), user2 still has 1
            # But user1 made a new call after reset, so 1
            assert stats['calls']['today'] == 2
            assert stats['calls']['all_time'] == 3  # Original 2 + new 1


class TestUserUsageDataClass:
    """Tests for UserUsage dataclass."""

    def test_user_usage_creation(self):
        """Test UserUsage creation with defaults."""
        usage = UserUsage(user_id='test_user')

        assert usage.user_id == 'test_user'
        assert usage.tier == 'free'
        assert usage.daily_calls == 0
        assert usage.total_calls == 0
        assert usage.last_reset is not None
        assert usage.last_call is None

    def test_user_usage_to_dict(self):
        """Test UserUsage to_dict method."""
        usage = UserUsage(user_id='test_user', tier='paid', daily_calls=10, total_calls=100)
        data = usage.to_dict()

        assert data['user_id'] == 'test_user'
        assert data['tier'] == 'paid'
        assert data['daily_calls'] == 10
        assert data['total_calls'] == 100
        assert data['last_reset'] is not None
        assert data['last_call'] is None


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_exactly_at_limit(self):
        """Test user exactly at the limit."""
        controller = CostController(limits={'free': 5, 'paid': 50})

        for _ in range(5):
            controller.record_api_call('user1')

        result = controller.check_limit('user1')

        assert result['allowed'] is False
        assert result['remaining'] == 0

    def test_negative_remaining_protection(self):
        """Test that remaining never goes negative."""
        controller = CostController(limits={'free': 1, 'paid': 10})

        controller.record_api_call('user1')
        controller.record_api_call('user1')  # This exceeds the limit

        usage = controller.get_user_usage('user1')
        # Remaining should be 0, not negative
        assert usage['remaining'] == 0

    def test_concurrent_users_isolation(self):
        """Test that users are isolated from each other."""
        controller = CostController()

        # User1 makes 10 calls
        for _ in range(10):
            controller.record_api_call('user1')

        # User2 makes 5 calls
        for _ in range(5):
            controller.record_api_call('user2')

        assert controller.get_user_usage('user1')['daily_calls'] == 10
        assert controller.get_user_usage('user2')['daily_calls'] == 5

        # User2 upgrades to paid
        controller.upgrade_tier('user2', 'paid')

        # User1 should still be free
        assert controller.get_user_usage('user1')['tier'] == 'free'
        assert controller.get_user_usage('user1')['daily_limit'] == 50

        # User2 should be paid
        assert controller.get_user_usage('user2')['tier'] == 'paid'
        assert controller.get_user_usage('user2')['daily_limit'] == 500

    def test_custom_limits_functionality(self):
        """Test that custom limits work correctly."""
        controller = CostController(limits={'free': 5, 'paid': 100, 'enterprise': 1000})

        # Free user
        assert controller.check_limit('free_user')['remaining'] == 5

        # Paid user
        controller.upgrade_tier('paid_user', 'paid')
        assert controller.check_limit('paid_user')['remaining'] == 100

        # Enterprise user
        controller.upgrade_tier('ent_user', 'enterprise')
        assert controller.check_limit('ent_user')['remaining'] == 1000