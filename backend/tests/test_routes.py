# backend/tests/test_routes.py
"""
Tests for REST API routes.
"""

import pytest
import json
from app import create_app


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Get a JWT token for authenticated requests."""
    # Register a user first
    register_data = {
        'username': 'testuser_routes',
        'password': 'password123',
        'email': 'test_routes@example.com'
    }
    client.post('/api/auth/register', json=register_data)

    # Login to get token
    login_data = {
        'username': 'testuser_routes',
        'password': 'password123'
    }
    response = client.post('/api/auth/login', json=login_data)
    data = json.loads(response.data)
    return data['data']['token']


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Test that health check returns status healthy."""
        response = client.get('/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestAuthRegister:
    """Tests for user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        user_data = {
            'username': 'newuser',
            'password': 'password123',
            'email': 'newuser@example.com'
        }

        response = client.post('/api/auth/register', json=user_data)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user_id' in data['data']
        assert data['data']['username'] == 'newuser'

    def test_register_missing_username(self, client):
        """Test registration with missing username."""
        user_data = {
            'password': 'password123',
            'email': 'test@example.com'
        }

        response = client.post('/api/auth/register', json=user_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_register_missing_password(self, client):
        """Test registration with missing password."""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }

        response = client.post('/api/auth/register', json=user_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_register_missing_email(self, client):
        """Test registration with missing email."""
        user_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        response = client.post('/api/auth/register', json=user_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        user_data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'invalidemail'
        }

        response = client.post('/api/auth/register', json=user_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_register_no_body(self, client):
        """Test registration with no request body."""
        response = client.post('/api/auth/register', json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestAuthLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client):
        """Test successful user login."""
        # Register first
        register_data = {
            'username': 'loginuser',
            'password': 'password123',
            'email': 'loginuser@example.com'
        }
        client.post('/api/auth/register', json=register_data)

        # Login
        login_data = {
            'username': 'loginuser',
            'password': 'password123'
        }

        response = client.post('/api/auth/login', json=login_data)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['username'] == 'loginuser'

    def test_login_missing_username(self, client):
        """Test login with missing username."""
        login_data = {
            'password': 'password123'
        }

        response = client.post('/api/auth/login', json=login_data)

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

    def test_login_missing_password(self, client):
        """Test login with missing password."""
        login_data = {
            'username': 'testuser'
        }

        response = client.post('/api/auth/login', json=login_data)

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

    def test_login_no_body(self, client):
        """Test login with no request body."""
        response = client.post('/api/auth/login', json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestChatEndpoint:
    """Tests for chat endpoint."""

    def test_chat_requires_jwt(self, client):
        """Test that chat endpoint requires JWT authentication."""
        chat_data = {
            'message': 'Hello'
        }

        response = client.post('/api/chat', json=chat_data)

        assert response.status_code == 401

    def test_chat_with_valid_jwt(self, client, auth_token):
        """Test chat with valid JWT token."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        chat_data = {
            'message': 'Hello, how are you?'
        }

        response = client.post('/api/chat', json=chat_data, headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'response' in data
        assert 'difficulty' in data
        assert 'mode' in data

    def test_chat_empty_message(self, client, auth_token):
        """Test chat with empty message."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        chat_data = {
            'message': ''
        }

        response = client.post('/api/chat', json=chat_data, headers=headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_chat_no_message(self, client, auth_token):
        """Test chat with no message field."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        chat_data = {}

        response = client.post('/api/chat', json=chat_data, headers=headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_chat_with_mode_override(self, client, auth_token):
        """Test chat with mode override."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        chat_data = {
            'message': 'Hello',
            'mode': 'practical'
        }

        response = client.post('/api/chat', json=chat_data, headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mode'] == 'practical'

    def test_chat_invalid_mode_override(self, client, auth_token):
        """Test chat with invalid mode override."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        chat_data = {
            'message': 'Hello',
            'mode': 'invalid_mode'
        }

        response = client.post('/api/chat', json=chat_data, headers=headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_chat_no_body(self, client, auth_token):
        """Test chat with no request body."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        response = client.post('/api/chat', headers=headers, json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestModeSwitchEndpoint:
    """Tests for mode switch endpoint."""

    def test_mode_switch_requires_jwt(self, client):
        """Test that mode switch endpoint requires JWT authentication."""
        mode_data = {
            'mode': 'practical'
        }

        response = client.post('/api/mode/switch', json=mode_data)

        assert response.status_code == 401

    def test_mode_switch_success(self, client, auth_token):
        """Test successful mode switch."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        mode_data = {
            'mode': 'practical'
        }

        response = client.post('/api/mode/switch', json=mode_data, headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['current_mode'] == 'practical'

    def test_mode_switch_to_teaching(self, client, auth_token):
        """Test switching to teaching mode."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        # First switch to practical
        client.post('/api/mode/switch', json={'mode': 'practical'}, headers=headers)

        # Then switch back to teaching
        mode_data = {
            'mode': 'teaching'
        }
        response = client.post('/api/mode/switch', json=mode_data, headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_mode'] == 'teaching'

    def test_mode_switch_invalid_mode(self, client, auth_token):
        """Test switching to invalid mode."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        mode_data = {
            'mode': 'invalid_mode'
        }

        response = client.post('/api/mode/switch', json=mode_data, headers=headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_mode_switch_missing_mode(self, client, auth_token):
        """Test mode switch with missing mode field."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        mode_data = {}

        response = client.post('/api/mode/switch', json=mode_data, headers=headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_mode_switch_no_body(self, client, auth_token):
        """Test mode switch with no request body."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        response = client.post('/api/mode/switch', headers=headers, json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestGetCurrentMode:
    """Tests for get current mode endpoint."""

    def test_get_mode_requires_jwt(self, client):
        """Test that get mode endpoint requires JWT authentication."""
        response = client.get('/api/mode/current')

        assert response.status_code == 401

    def test_get_mode_success(self, client, auth_token):
        """Test successful get current mode."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        response = client.get('/api/mode/current', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'current_mode' in data
        assert data['current_mode'] in ['teaching', 'practical']
        assert 'config' in data

    def test_get_mode_after_switch(self, client, auth_token):
        """Test get current mode after switching."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        # Switch mode first
        client.post('/api/mode/switch', json={'mode': 'practical'}, headers=headers)

        # Get current mode
        response = client.get('/api/mode/current', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_mode'] == 'practical'


class TestIntegration:
    """Integration tests for full API flow."""

    def test_full_user_flow(self, client):
        """Test complete user registration, login, and chat flow."""
        # Register
        register_data = {
            'username': 'flowuser',
            'password': 'password123',
            'email': 'flowuser@example.com'
        }
        response = client.post('/api/auth/register', json=register_data)
        assert response.status_code == 201

        # Login
        login_data = {
            'username': 'flowuser',
            'password': 'password123'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        data = json.loads(response.data)
        token = data['data']['token']

        headers = {'Authorization': f'Bearer {token}'}

        # Get current mode (should be teaching by default)
        response = client.get('/api/mode/current', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_mode'] == 'teaching'

        # Switch mode
        response = client.post('/api/mode/switch', json={'mode': 'practical'}, headers=headers)
        assert response.status_code == 200

        # Chat
        response = client.post('/api/chat', json={'message': 'Hello'}, headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mode'] == 'practical'

    def test_multiple_users_have_separate_sessions(self, client):
        """Test that multiple users have separate mode sessions."""
        # Register and login user1
        user1_register = {
            'username': 'user1',
            'password': 'password123',
            'email': 'user1@example.com'
        }
        client.post('/api/auth/register', json=user1_register)
        response = client.post('/api/auth/login', json={'username': 'user1', 'password': 'password123'})
        token1 = json.loads(response.data)['data']['token']

        # Register and login user2
        user2_register = {
            'username': 'user2',
            'password': 'password123',
            'email': 'user2@example.com'
        }
        client.post('/api/auth/register', json=user2_register)
        response = client.post('/api/auth/login', json={'username': 'user2', 'password': 'password123'})
        token2 = json.loads(response.data)['data']['token']

        headers1 = {'Authorization': f'Bearer {token1}'}
        headers2 = {'Authorization': f'Bearer {token2}'}

        # User1 switches to practical
        client.post('/api/mode/switch', json={'mode': 'practical'}, headers=headers1)

        # User2 should still be in teaching mode
        response = client.get('/api/mode/current', headers=headers2)
        data = json.loads(response.data)
        assert data['current_mode'] == 'teaching'

        # User1 should be in practical mode
        response = client.get('/api/mode/current', headers=headers1)
        data = json.loads(response.data)
        assert data['current_mode'] == 'practical'


class TestCacheEndpoints:
    """Tests for cache management endpoints."""

    def test_cache_stats_requires_jwt(self, client):
        """Test that cache stats endpoint requires JWT authentication."""
        response = client.get('/api/cache/stats')

        assert response.status_code == 401

    def test_cache_stats_success(self, client, auth_token):
        """Test successful cache stats retrieval."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        response = client.get('/api/cache/stats', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'stats' in data
        assert 'total_entries' in data['stats']
        assert 'hits' in data['stats']
        assert 'misses' in data['stats']
        assert 'hit_rate' in data['stats']

    def test_cache_clear_requires_jwt(self, client):
        """Test that cache clear endpoint requires JWT authentication."""
        response = client.post('/api/cache/clear')

        assert response.status_code == 401

    def test_cache_clear_success(self, client, auth_token):
        """Test successful cache clear."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        response = client.post('/api/cache/clear', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_cache_clear_expired_requires_jwt(self, client):
        """Test that cache clear expired endpoint requires JWT authentication."""
        response = client.post('/api/cache/clear-expired')

        assert response.status_code == 401

    def test_cache_clear_expired_success(self, client, auth_token):
        """Test successful cache expired clear."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        response = client.post('/api/cache/clear-expired', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_chat_with_cached_response(self, client, auth_token):
        """Test that chat returns cached response on repeated requests."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        chat_data = {
            'message': 'Test caching message'
        }

        # First request - should not be cached
        response1 = client.post('/api/chat', json=chat_data, headers=headers)
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1['cached'] is False

        # Second identical request - should be cached
        response2 = client.post('/api/chat', json=chat_data, headers=headers)
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['cached'] is True
        assert data2['response'] == data1['response']

    def test_cache_hit_rate_after_requests(self, client, auth_token):
        """Test that cache stats reflect hit rate after requests."""
        headers = {'Authorization': f'Bearer {auth_token}'}

        # Make a chat request
        client.post('/api/chat', json={'message': 'Cache test'}, headers=headers)

        # Make same request again (should be cached)
        client.post('/api/chat', json={'message': 'Cache test'}, headers=headers)

        # Check cache stats
        response = client.get('/api/cache/stats', headers=headers)
        data = json.loads(response.data)
        assert data['stats']['hits'] >= 1
        assert data['stats']['total_entries'] >= 1