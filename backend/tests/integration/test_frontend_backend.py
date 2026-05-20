# backend/tests/integration/test_frontend_backend.py
"""
Frontend-Backend integration tests.

Tests the complete flow between frontend and backend components.
Uses Flask's test client for reliable testing without starting a real server.
"""

import pytest
import json
from app import create_app


@pytest.fixture(scope="class")
def app():
    """Create a Flask app for integration testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-for-integration-tests'
    yield app


@pytest.fixture(scope="class")
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Get a JWT token for authenticated requests."""
    unique_id = str(int(__import__('time').time() * 1000))[-6:]  # Use last 6 digits to keep username short
    register_data = {
        'username': f'integ_{unique_id}',
        'password': 'testPassword123',
        'email': f'integ_{unique_id}@test.com'
    }
    client.post('/api/auth/register', json=register_data)

    login_data = {
        'username': register_data['username'],
        'password': register_data['password']
    }
    response = client.post('/api/auth/login', json=login_data)
    data = json.loads(response.data)
    return data['data']['token'], register_data['username']


class TestHealthCheckIntegration:
    """Tests for health check endpoint integration."""

    def test_health_check_integration(self, client):
        """Test that health check endpoint returns healthy status."""
        response = client.get('/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_health_check_response_format(self, client):
        """Test that health check returns correct response format."""
        response = client.get('/health')

        assert response.headers.get('Content-Type', '').startswith('application/json')
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert 'status' in data


class TestAuthIntegration:
    """Tests for authentication flow integration."""

    def test_register_login_integration(self, client):
        """Test complete registration and login flow."""
        unique_id = str(int(__import__('time').time() * 1000))[-6:]  # Use last 6 digits

        # Step 1: Register a new user
        register_data = {
            'username': f'flow_{unique_id}',
            'password': 'testPassword123',
            'email': f'flow_{unique_id}@test.com'
        }

        register_response = client.post('/api/auth/register', json=register_data)

        assert register_response.status_code == 201
        register_json = json.loads(register_response.data)
        assert register_json['success'] is True
        assert 'user_id' in register_json['data']
        assert register_json['data']['username'] == register_data['username']

        # Step 2: Login with the registered user
        login_data = {
            'username': register_data['username'],
            'password': register_data['password']
        }

        login_response = client.post('/api/auth/login', json=login_data)

        assert login_response.status_code == 200
        login_json = json.loads(login_response.data)
        assert login_json['success'] is True
        assert 'token' in login_json['data']
        assert login_json['data']['username'] == register_data['username']

        # Verify token format (should be a non-empty string)
        token = login_json['data']['token']
        assert isinstance(token, str)
        assert len(token) > 0

    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        # Missing password
        response = client.post('/api/auth/login', json={'username': 'testuser'})
        assert response.status_code == 401

        # Missing username
        response = client.post('/api/auth/login', json={'password': 'testpassword'})
        assert response.status_code == 401

        # Empty body
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400


class TestChatFlowIntegration:
    """Tests for chat flow integration."""

    def test_chat_flow_integration(self, client, auth_token):
        """Test complete chat flow."""
        token, username = auth_token
        headers = {'Authorization': f'Bearer {token}'}

        # Step 1: Send a chat message
        chat_data = {
            'message': 'Hello, I want to learn programming'
        }

        response = client.post('/api/chat', json=chat_data, headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'response' in data
        assert 'difficulty' in data
        assert 'mode' in data

        # Step 2: Send another message to continue conversation
        follow_up_data = {
            'message': 'Can you help me with Python?'
        }

        response = client.post('/api/chat', json=follow_up_data, headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_chat_requires_authentication(self, client):
        """Test that chat endpoint requires JWT authentication."""
        chat_data = {
            'message': 'Hello'
        }

        response = client.post('/api/chat', json=chat_data)

        assert response.status_code == 401

    def test_chat_invalid_token(self, client):
        """Test chat with invalid JWT token."""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        chat_data = {
            'message': 'Hello'
        }

        response = client.post('/api/chat', json=chat_data, headers=headers)

        assert response.status_code in [401, 422]

    def test_chat_empty_message(self, client, auth_token):
        """Test chat with empty message."""
        token, _ = auth_token
        headers = {'Authorization': f'Bearer {token}'}

        response = client.post('/api/chat', json={'message': ''}, headers=headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_chat_missing_message(self, client, auth_token):
        """Test chat with missing message field."""
        token, _ = auth_token
        headers = {'Authorization': f'Bearer {token}'}

        response = client.post('/api/chat', json={}, headers=headers)

        assert response.status_code == 400


class TestErrorHandlingIntegration:
    """Tests for error handling across the API."""

    def test_error_handling_nonexistent_endpoint(self, client):
        """Test API error handling for nonexistent endpoints."""
        response = client.get('/api/nonexistent')

        assert response.status_code == 404

    def test_error_handling_wrong_method(self, client):
        """Test API error handling for wrong HTTP method."""
        response = client.delete('/health')

        assert response.status_code == 405

    def test_register_validation_errors(self, client):
        """Test registration validation error responses."""
        # Missing username
        response = client.post(
            '/api/auth/register',
            json={'password': 'test123', 'email': 'test@test.com'}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data or 'message' in data

        # Missing password
        response = client.post(
            '/api/auth/register',
            json={'username': 'testuser', 'email': 'test@test.com'}
        )
        assert response.status_code == 400

        # Missing email
        response = client.post(
            '/api/auth/register',
            json={'username': 'testuser', 'password': 'test123'}
        )
        assert response.status_code == 400

        # Invalid email format
        response = client.post(
            '/api/auth/register',
            json={'username': 'testuser', 'password': 'test123', 'email': 'invalid-email'}
        )
        assert response.status_code == 400

    def test_unauthenticated_requests_protected_endpoints(self, client):
        """Test that protected endpoints return 401 without authentication."""
        # Chat endpoint
        response = client.post('/api/chat', json={'message': 'Hello'})
        assert response.status_code == 401

        # Mode switch endpoint
        response = client.post('/api/mode/switch', json={'mode': 'practical'})
        assert response.status_code == 401

        # Get current mode endpoint
        response = client.get('/api/mode/current')
        assert response.status_code == 401


class TestResponseFormatIntegration:
    """Tests for API response format consistency."""

    def test_register_response_format(self, client):
        """Test registration response format."""
        unique_id = str(int(__import__('time').time() * 1000))[-6:]  # Use last 6 digits

        response = client.post(
            '/api/auth/register',
            json={
                'username': f'reg_{unique_id}',
                'password': 'testPassword123',
                'email': f'reg_{unique_id}@test.com'
            }
        )

        assert response.status_code == 201
        data = json.loads(response.data)

        # Check response structure
        assert 'success' in data
        assert 'message' in data or 'data' in data

        if data['success']:
            assert 'user_id' in data['data']
            assert 'username' in data['data']

    def test_login_response_format(self, client):
        """Test login response format."""
        unique_id = str(int(__import__('time').time() * 1000))[-6:]  # Use last 6 digits
        username = f'login_{unique_id}'

        # Register first
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'testPassword123',
                'email': f'{username}@test.com'
            }
        )

        # Login
        response = client.post(
            '/api/auth/login',
            json={
                'username': username,
                'password': 'testPassword123'
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'data' in data
        assert 'token' in data['data']
        assert 'username' in data['data']
        assert 'user_id' in data['data']

    def test_chat_response_format(self, client, auth_token):
        """Test chat response format."""
        token, _ = auth_token
        headers = {'Authorization': f'Bearer {token}'}

        response = client.post(
            '/api/chat',
            json={'message': 'Test message'},
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'response' in data
        assert 'difficulty' in data
        assert 'mode' in data

        # Check types
        assert isinstance(data['response'], str)
        assert isinstance(data['difficulty'], str)
        assert isinstance(data['mode'], str)

    def test_mode_switch_response_format(self, client, auth_token):
        """Test mode switch response format."""
        token, _ = auth_token
        headers = {'Authorization': f'Bearer {token}'}

        response = client.post(
            '/api/mode/switch',
            json={'mode': 'practical'},
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'current_mode' in data
        assert data['current_mode'] == 'practical'

    def test_get_mode_response_format(self, client, auth_token):
        """Test get current mode response format."""
        token, _ = auth_token
        headers = {'Authorization': f'Bearer {token}'}

        response = client.get('/api/mode/current', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'current_mode' in data
        assert 'config' in data
        assert data['current_mode'] in ['teaching', 'practical']
        assert isinstance(data['config'], dict)

    def test_error_response_format(self, client):
        """Test error response format."""
        response = client.post(
            '/api/auth/register',
            json={'username': 'a', 'password': '123', 'email': 'invalid'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)

        # Check error response structure
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data or 'message' in data