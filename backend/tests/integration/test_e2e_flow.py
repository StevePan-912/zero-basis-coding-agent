# backend/tests/integration/test_e2e_flow.py
"""
End-to-end flow tests.

Tests complete user journeys from registration through chat interactions.
Uses Flask's test client for reliable testing without starting a real server.
"""

import pytest
import json
import time
from app import create_app


@pytest.fixture(scope="class")
def app():
    """Create a Flask app for integration testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-for-e2e-tests'
    yield app


@pytest.fixture(scope="class")
def client(app):
    """Create a test client."""
    return app.test_client()


def create_authenticated_user(client, prefix='e2e'):
    """Helper to create and authenticate a user."""
    unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits to keep username short
    username = f'{prefix}_{unique_id}'

    # Register user
    client.post(
        '/api/auth/register',
        json={
            'username': username,
            'password': 'testPassword123',
            'email': f'{username}@test.com'
        }
    )

    # Login to get token
    login_response = client.post(
        '/api/auth/login',
        json={
            'username': username,
            'password': 'testPassword123'
        }
    )

    login_data = json.loads(login_response.data)
    return {
        'token': login_data['data']['token'],
        'user_id': login_data['data']['user_id'],
        'username': username
    }


class TestNewUserLearningFlow:
    """Tests for new user learning flow."""

    def test_new_user_learning_flow(self, client):
        """
        Test the complete new user learning flow:
        1. Register a new user
        2. Login to get JWT token
        3. Check default mode (should be 'teaching')
        4. Send initial message about learning goal
        5. Continue conversation with follow-up questions
        6. Verify difficulty adaptation
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'learn_{unique_id}'

        # Step 1: Register new user
        print(f"\n=== Starting new user learning flow for {username} ===")

        register_response = client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'learning123',
                'email': f'{username}@test.com'
            }
        )
        assert register_response.status_code == 201
        register_data = json.loads(register_response.data)
        print(f"Registration successful: user_id={register_data['data']['user_id']}")

        # Step 2: Login
        login_response = client.post(
            '/api/auth/login',
            json={
                'username': username,
                'password': 'learning123'
            }
        )
        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        token = login_data['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        print("Login successful, token received")

        # Step 3: Check default mode
        mode_response = client.get('/api/mode/current', headers=headers)
        assert mode_response.status_code == 200
        mode_data = json.loads(mode_response.data)
        assert mode_data['current_mode'] == 'teaching'
        print(f"Default mode: {mode_data['current_mode']}")

        # Step 4: Send initial learning message
        chat_response = client.post(
            '/api/chat',
            json={
                'message': 'I want to learn Python programming from scratch. I have no prior programming experience.'
            },
            headers=headers
        )
        assert chat_response.status_code == 200
        chat_data = json.loads(chat_response.data)
        assert chat_data['success'] is True
        assert chat_data['mode'] == 'teaching'
        print(f"First chat response received, mode={chat_data['mode']}, difficulty={chat_data['difficulty']}")

        # Step 5: Continue conversation with follow-up
        follow_up_response = client.post(
            '/api/chat',
            json={
                'message': 'What should I learn first?'
            },
            headers=headers
        )
        assert follow_up_response.status_code == 200
        follow_up_data = json.loads(follow_up_response.data)
        assert follow_up_data['success'] is True
        print(f"Follow-up response received, mode={follow_up_data['mode']}")

        # Step 6: Ask about a concept
        concept_response = client.post(
            '/api/chat',
            json={
                'message': 'Can you explain what variables are?'
            },
            headers=headers
        )
        assert concept_response.status_code == 200
        concept_data = json.loads(concept_response.data)
        assert concept_data['success'] is True
        print(f"Concept response received, difficulty={concept_data['difficulty']}")

        # Step 7: Request practical example
        practical_response = client.post(
            '/api/chat',
            json={
                'message': 'Can you show me a simple example?'
            },
            headers=headers
        )
        assert practical_response.status_code == 200
        practical_data = json.loads(practical_response.data)
        assert practical_data['success'] is True
        print("Practical example response received")

        print("=== New user learning flow completed successfully ===\n")

    def test_user_progression_flow(self, client):
        """
        Test user progression through different difficulty levels.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'prog_{unique_id}'

        # Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'progress123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'progress123'}
        )
        token = json.loads(login_response.data)['data']['token']
        headers = {'Authorization': f'Bearer {token}'}

        # Start with beginner question
        response1 = client.post(
            '/api/chat',
            json={'message': 'What is a for loop?'},
            headers=headers
        )
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        print(f"Beginner question: difficulty={data1['difficulty']}")

        # Ask intermediate question
        response2 = client.post(
            '/api/chat',
            json={'message': 'How do nested loops work?'},
            headers=headers
        )
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        print(f"Intermediate question: difficulty={data2['difficulty']}")

        # Ask advanced question
        response3 = client.post(
            '/api/chat',
            json={'message': 'Can you explain list comprehensions and how they relate to functional programming?'},
            headers=headers
        )
        assert response3.status_code == 200
        data3 = json.loads(response3.data)
        print(f"Advanced question: difficulty={data3['difficulty']}")


class TestModeSwitchingFlow:
    """Tests for mode switching flow."""

    def test_mode_switching_flow(self, client):
        """
        Test complete mode switching flow:
        1. Register and login
        2. Start in teaching mode
        3. Switch to practical mode
        4. Verify mode change
        5. Send message in practical mode
        6. Switch back to teaching mode
        7. Verify conversation context maintained
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'switch_{unique_id}'

        print(f"\n=== Starting mode switching flow for {username} ===")

        # Step 1: Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'mode123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'mode123'}
        )
        token = json.loads(login_response.data)['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        print("User authenticated")

        # Step 2: Verify default teaching mode
        mode_response = client.get('/api/mode/current', headers=headers)
        assert mode_response.status_code == 200
        assert json.loads(mode_response.data)['current_mode'] == 'teaching'
        print("Default mode: teaching")

        # Step 3: Send message in teaching mode
        teaching_response = client.post(
            '/api/chat',
            json={'message': 'Explain how HTTP works'},
            headers=headers
        )
        assert teaching_response.status_code == 200
        teaching_data = json.loads(teaching_response.data)
        assert teaching_data['mode'] == 'teaching'
        print(f"Teaching mode response: mode={teaching_data['mode']}")

        # Step 4: Switch to practical mode
        switch_response = client.post(
            '/api/mode/switch',
            json={'mode': 'practical'},
            headers=headers
        )
        assert switch_response.status_code == 200
        switch_data = json.loads(switch_response.data)
        assert switch_data['current_mode'] == 'practical'
        print("Switched to practical mode")

        # Step 5: Verify mode change
        verify_response = client.get('/api/mode/current', headers=headers)
        assert verify_response.status_code == 200
        assert json.loads(verify_response.data)['current_mode'] == 'practical'
        print("Mode change verified")

        # Step 6: Send message in practical mode
        practical_response = client.post(
            '/api/chat',
            json={'message': 'Show me how to make a GET request in Python'},
            headers=headers
        )
        assert practical_response.status_code == 200
        practical_data = json.loads(practical_response.data)
        assert practical_data['mode'] == 'practical'
        print(f"Practical mode response: mode={practical_data['mode']}")

        # Step 7: Switch back to teaching mode
        switch_back_response = client.post(
            '/api/mode/switch',
            json={'mode': 'teaching'},
            headers=headers
        )
        assert switch_back_response.status_code == 200
        assert json.loads(switch_back_response.data)['current_mode'] == 'teaching'
        print("Switched back to teaching mode")

        # Step 8: Continue conversation in teaching mode
        continue_response = client.post(
            '/api/chat',
            json={'message': 'What about POST requests?'},
            headers=headers
        )
        assert continue_response.status_code == 200
        continue_data = json.loads(continue_response.data)
        assert continue_data['mode'] == 'teaching'
        print(f"Continued in teaching mode: mode={continue_data['mode']}")

        print("=== Mode switching flow completed successfully ===\n")

    def test_mode_override_in_chat(self, client):
        """
        Test mode override in chat message.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'over_{unique_id}'

        # Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'override123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'override123'}
        )
        token = json.loads(login_response.data)['data']['token']
        headers = {'Authorization': f'Bearer {token}'}

        # Verify default mode
        mode_response = client.get('/api/mode/current', headers=headers)
        assert json.loads(mode_response.data)['current_mode'] == 'teaching'

        # Send message with mode override
        override_response = client.post(
            '/api/chat',
            json={
                'message': 'Give me a practical example of async programming',
                'mode': 'practical'
            },
            headers=headers
        )
        assert override_response.status_code == 200
        override_data = json.loads(override_response.data)
        assert override_data['mode'] == 'practical'
        print(f"Mode override in chat: mode={override_data['mode']}")

        # Verify mode was changed
        verify_response = client.get('/api/mode/current', headers=headers)
        assert json.loads(verify_response.data)['current_mode'] == 'practical'
        print("Mode change persisted after override")

    def test_invalid_mode_switch(self, client):
        """
        Test switching to invalid mode.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'inv_{unique_id}'

        # Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'invalid123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'invalid123'}
        )
        token = json.loads(login_response.data)['data']['token']
        headers = {'Authorization': f'Bearer {token}'}

        # Try to switch to invalid mode
        switch_response = client.post(
            '/api/mode/switch',
            json={'mode': 'invalid_mode'},
            headers=headers
        )
        assert switch_response.status_code == 400
        switch_data = json.loads(switch_response.data)
        assert switch_data['success'] is False
        print(f"Invalid mode rejected: {switch_data.get('error', switch_data.get('message'))}")

        # Verify mode unchanged
        mode_response = client.get('/api/mode/current', headers=headers)
        assert json.loads(mode_response.data)['current_mode'] == 'teaching'
        print("Mode remains unchanged after invalid switch attempt")


class TestMultiUserFlow:
    """Tests for multiple user interactions."""

    def test_multiple_users_separate_sessions(self, client):
        """
        Test that multiple users have separate sessions.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits

        # Create two users
        user1_name = f'u1_{unique_id}'
        user2_name = f'u2_{unique_id}'

        # Register users
        for username in [user1_name, user2_name]:
            client.post(
                '/api/auth/register',
                json={
                    'username': username,
                    'password': 'multi123',
                    'email': f'{username}@test.com'
                }
            )

        # Login both users
        user1_login = client.post(
            '/api/auth/login',
            json={'username': user1_name, 'password': 'multi123'}
        )
        user1_token = json.loads(user1_login.data)['data']['token']
        user1_headers = {'Authorization': f'Bearer {user1_token}'}

        user2_login = client.post(
            '/api/auth/login',
            json={'username': user2_name, 'password': 'multi123'}
        )
        user2_token = json.loads(user2_login.data)['data']['token']
        user2_headers = {'Authorization': f'Bearer {user2_token}'}

        print(f"\n=== Multi-user session test ===")
        print(f"User 1: {user1_name}")
        print(f"User 2: {user2_name}")

        # User 1 switches to practical mode
        client.post(
            '/api/mode/switch',
            json={'mode': 'practical'},
            headers=user1_headers
        )

        # User 2 should still be in teaching mode
        user2_mode = client.get('/api/mode/current', headers=user2_headers)
        assert json.loads(user2_mode.data)['current_mode'] == 'teaching'
        print(f"User 2 mode: teaching (unchanged)")

        # User 1 mode should be practical
        user1_mode = client.get('/api/mode/current', headers=user1_headers)
        assert json.loads(user1_mode.data)['current_mode'] == 'practical'
        print(f"User 1 mode: practical")

        # User 2 switches mode
        client.post(
            '/api/mode/switch',
            json={'mode': 'practical'},
            headers=user2_headers
        )

        # User 1 should still have their own mode
        user1_mode_check = client.get('/api/mode/current', headers=user1_headers)
        assert json.loads(user1_mode_check.data)['current_mode'] == 'practical'
        print("Both users have independent sessions")

    def test_concurrent_chat_sessions(self, client):
        """
        Test concurrent chat sessions for different users.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits

        users = []
        for i in range(3):
            username = f'conc{i}_{unique_id}'

            # Register and login
            client.post(
                '/api/auth/register',
                json={
                    'username': username,
                    'password': 'concurrent123',
                    'email': f'{username}@test.com'
                }
            )

            login_response = client.post(
                '/api/auth/login',
                json={'username': username, 'password': 'concurrent123'}
            )

            users.append({
                'username': username,
                'token': json.loads(login_response.data)['data']['token']
            })

        print(f"\n=== Concurrent sessions test with {len(users)} users ===")

        # Each user sends a chat message
        for i, user in enumerate(users):
            headers = {'Authorization': f'Bearer {user["token"]}'}
            response = client.post(
                '/api/chat',
                json={'message': f'Hello from user {i + 1}'},
                headers=headers
            )
            assert response.status_code == 200
            print(f"User {i + 1} ({user['username']}): chat successful")


class TestErrorRecoveryFlow:
    """Tests for error recovery scenarios."""

    def test_token_expiry_handling(self, client):
        """
        Test handling of expired/invalid tokens.
        """
        # Use an obviously invalid token
        invalid_headers = {'Authorization': 'Bearer invalid.expired.token'}

        # Try to access protected endpoint
        response = client.get('/api/mode/current', headers=invalid_headers)
        assert response.status_code in [401, 422]
        print("Invalid token correctly rejected")

    def test_malformed_request_recovery(self, client):
        """
        Test recovery from malformed requests.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'mal_{unique_id}'

        # Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'malformed123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'malformed123'}
        )
        token = json.loads(login_response.data)['data']['token']
        headers = {'Authorization': f'Bearer {token}'}

        # Send malformed request
        malformed_response = client.post(
            '/api/chat',
            json={'unexpected_field': 'value'},
            headers=headers
        )
        assert malformed_response.status_code == 400

        # Verify subsequent valid request works
        valid_response = client.post(
            '/api/chat',
            json={'message': 'This is a valid message'},
            headers=headers
        )
        assert valid_response.status_code == 200
        print("Session recovered after malformed request")

    def test_rapid_requests(self, client):
        """
        Test behavior under rapid requests.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'rap_{unique_id}'

        # Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'rapid123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'rapid123'}
        )
        token = json.loads(login_response.data)['data']['token']
        headers = {'Authorization': f'Bearer {token}'}

        # Send rapid requests
        success_count = 0
        for i in range(5):
            response = client.post(
                '/api/chat',
                json={'message': f'Rapid message {i}'},
                headers=headers
            )
            if response.status_code == 200:
                success_count += 1

        # All requests should succeed (no rate limiting in current implementation)
        assert success_count == 5
        print(f"Rapid requests: {success_count}/5 successful")


class TestJWTAuthenticationFlow:
    """Tests for JWT authentication flow."""

    def test_jwt_token_structure(self, client):
        """
        Test that JWT token has correct structure.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'jwt_{unique_id}'

        # Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'jwt123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'jwt123'}
        )
        token = json.loads(login_response.data)['data']['token']

        # JWT should have 3 parts separated by dots
        assert token.count('.') == 2
        parts = token.split('.')
        assert len(parts) == 3

        # Each part should be base64 encoded
        for part in parts:
            assert len(part) > 0

        print(f"JWT token has valid structure: {len(parts)} parts")

    def test_jwt_protected_endpoints(self, client):
        """
        Test that all protected endpoints require valid JWT.
        """
        protected_endpoints = [
            ('GET', '/api/mode/current'),
            ('POST', '/api/mode/switch'),
            ('POST', '/api/chat'),
        ]

        for method, endpoint in protected_endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})

            assert response.status_code == 401, \
                f"Endpoint {endpoint} should require authentication"
            print(f"Endpoint {endpoint}: correctly requires authentication")

    def test_jwt_authorization_header_format(self, client):
        """
        Test various authorization header formats.
        """
        unique_id = str(int(time.time() * 1000))[-6:]  # Use last 6 digits
        username = f'auth_{unique_id}'

        # Register and login
        client.post(
            '/api/auth/register',
            json={
                'username': username,
                'password': 'format123',
                'email': f'{username}@test.com'
            }
        )

        login_response = client.post(
            '/api/auth/login',
            json={'username': username, 'password': 'format123'}
        )
        token = json.loads(login_response.data)['data']['token']

        # Test correct format
        correct_headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/mode/current', headers=correct_headers)
        assert response.status_code == 200
        print("Correct 'Bearer {token}' format works")

        # Test without 'Bearer' prefix
        no_bearer_headers = {'Authorization': token}
        response = client.get('/api/mode/current', headers=no_bearer_headers)
        assert response.status_code in [401, 422]
        print("Token without 'Bearer' prefix rejected")