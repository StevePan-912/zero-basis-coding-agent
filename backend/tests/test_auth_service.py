# backend/tests/test_auth_service.py
"""
Tests for AuthService and JWTHandler classes.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import time
import jwt

from app.auth import AuthService, AuthResult, JWTHandler
from app.config import Config


class TestJWTHandler:
    """Tests for JWTHandler class."""

    def test_generate_token_returns_string(self):
        """Test that generate_token returns a string."""
        token = JWTHandler.generate_token('user123', 'testuser')

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_contains_user_info(self):
        """Test that generated token contains user information."""
        user_id = 'user123'
        username = 'testuser'

        token = JWTHandler.generate_token(user_id, username)
        payload = JWTHandler.verify_token(token)

        assert payload is not None
        assert payload['user_id'] == user_id
        assert payload['username'] == username

    def test_verify_token_valid_token(self):
        """Test verifying a valid token."""
        token = JWTHandler.generate_token('user123', 'testuser')
        payload = JWTHandler.verify_token(token)

        assert payload is not None
        assert 'user_id' in payload
        assert 'username' in payload
        assert 'exp' in payload
        assert 'iat' in payload

    def test_verify_token_invalid_token(self):
        """Test verifying an invalid token returns None."""
        invalid_token = "invalid.token.string"
        payload = JWTHandler.verify_token(invalid_token)

        assert payload is None

    def test_verify_token_tampered_token(self):
        """Test verifying a tampered token returns None."""
        token = JWTHandler.generate_token('user123', 'testuser')
        # Tamper with the token
        tampered = token[:-5] + 'xxxxx'
        payload = JWTHandler.verify_token(tampered)

        assert payload is None

    def test_verify_token_expired_token(self):
        """Test verifying an expired token returns None."""
        # Create an expired token manually
        now = datetime.now(timezone.utc)
        past_time = now - timedelta(hours=1)

        payload = {
            'user_id': 'user123',
            'username': 'testuser',
            'iat': past_time - timedelta(hours=2),
            'exp': past_time
        }

        expired_token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        result = JWTHandler.verify_token(expired_token)
        assert result is None

    def test_decode_token_without_expiry_verification(self):
        """Test decoding token without verifying expiry."""
        # Create an expired token
        now = datetime.now(timezone.utc)
        past_time = now - timedelta(hours=1)

        payload = {
            'user_id': 'user123',
            'username': 'testuser',
            'iat': past_time - timedelta(hours=2),
            'exp': past_time
        }

        expired_token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        # decode_token should still return payload even for expired token
        decoded = JWTHandler.decode_token(expired_token)

        assert decoded is not None
        assert decoded['user_id'] == 'user123'
        assert decoded['username'] == 'testuser'

    def test_decode_token_invalid_format(self):
        """Test decoding an invalid token format returns None."""
        invalid_token = "not-a-valid-jwt"
        result = JWTHandler.decode_token(invalid_token)

        assert result is None

    def test_token_expiry_uses_config(self):
        """Test that token expiry uses Config.JWT_ACCESS_TOKEN_EXPIRES."""
        original_expiry = Config.JWT_ACCESS_TOKEN_EXPIRES

        token = JWTHandler.generate_token('user123', 'testuser')
        payload = JWTHandler.verify_token(token)

        assert payload is not None

        # Check that expiry is approximately correct (within a few seconds tolerance)
        exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(seconds=original_expiry)

        # Allow 5 seconds tolerance
        diff = abs((exp_time - expected_exp).total_seconds())
        assert diff < 5


class TestAuthService:
    """Tests for AuthService class."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        hashed = AuthService.hash_password('password123')

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != 'password123'

    def test_hash_password_different_salts(self):
        """Test that same password produces different hashes."""
        hash1 = AuthService.hash_password('password123')
        hash2 = AuthService.hash_password('password123')

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = 'password123'
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = 'password123'
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password('wrongpassword', hashed) is False

    def test_verify_password_invalid_hash(self):
        """Test verifying password with invalid hash format."""
        result = AuthService.verify_password('password123', 'invalid_hash')
        assert result is False


class TestAuthServiceRegistration:
    """Tests for user registration functionality."""

    def test_register_user_mock_mode(self):
        """Test user registration in mock mode."""
        user_data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data, mock=True)

        assert result.success is True
        assert 'mock mode' in result.message.lower()
        assert result.data['username'] == 'testuser'
        assert result.data['email'] == 'test@example.com'
        assert 'user_id' in result.data

    def test_register_user_success(self):
        """Test successful user registration."""
        user_data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data, mock=False)

        assert result.success is True
        assert result.data['username'] == 'testuser'
        assert result.data['email'] == 'test@example.com'
        assert 'user_id' in result.data
        assert 'hashed_password' in result.data

    def test_register_user_username_too_short(self):
        """Test registration with username too short."""
        user_data = {
            'username': 'ab',  # Less than 3 characters
            'password': 'password123',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert '3' in result.error

    def test_register_user_username_too_long(self):
        """Test registration with username too long."""
        user_data = {
            'username': 'a' * 21,  # More than 20 characters
            'password': 'password123',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert '20' in result.error

    def test_register_user_username_missing(self):
        """Test registration without username."""
        user_data = {
            'password': 'password123',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert 'username' in result.error.lower()

    def test_register_user_password_too_short(self):
        """Test registration with password too short."""
        user_data = {
            'username': 'testuser',
            'password': '12345',  # Less than 6 characters
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert '6' in result.error

    def test_register_user_password_missing(self):
        """Test registration without password."""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert 'password' in result.error.lower()

    def test_register_user_email_missing(self):
        """Test registration without email."""
        user_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert 'email' in result.error.lower()

    def test_register_user_email_invalid_no_at(self):
        """Test registration with email missing @."""
        user_data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'testexample.com'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert 'email' in result.error.lower()

    def test_register_user_email_invalid_no_dot(self):
        """Test registration with email missing dot."""
        user_data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@examplecom'
        }

        result = AuthService.register_user(user_data)

        assert result.success is False
        assert 'email' in result.error.lower()

    def test_register_user_min_username_length(self):
        """Test registration with minimum username length."""
        user_data = {
            'username': 'abc',  # Exactly 3 characters
            'password': 'password123',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data, mock=True)

        assert result.success is True

    def test_register_user_max_username_length(self):
        """Test registration with maximum username length."""
        user_data = {
            'username': 'a' * 20,  # Exactly 20 characters
            'password': 'password123',
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data, mock=True)

        assert result.success is True

    def test_register_user_min_password_length(self):
        """Test registration with minimum password length."""
        user_data = {
            'username': 'testuser',
            'password': '123456',  # Exactly 6 characters
            'email': 'test@example.com'
        }

        result = AuthService.register_user(user_data, mock=True)

        assert result.success is True


class TestAuthServiceLogin:
    """Tests for user login functionality."""

    def test_login_user_mock_mode(self):
        """Test user login in mock mode."""
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        result = AuthService.login_user(login_data, mock=True)

        assert result.success is True
        assert 'mock mode' in result.message.lower()
        assert 'token' in result.data
        assert result.data['username'] == 'testuser'

    def test_login_user_success(self):
        """Test successful user login."""
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        result = AuthService.login_user(login_data, mock=False)

        assert result.success is True
        assert 'token' in result.data
        assert result.data['username'] == 'testuser'

    def test_login_user_missing_username(self):
        """Test login with missing username."""
        login_data = {
            'password': 'password123'
        }

        result = AuthService.login_user(login_data)

        assert result.success is False
        assert 'username' in result.error.lower()

    def test_login_user_missing_password(self):
        """Test login with missing password."""
        login_data = {
            'username': 'testuser'
        }

        result = AuthService.login_user(login_data)

        assert result.success is False
        assert 'password' in result.error.lower()

    def test_login_user_empty_username(self):
        """Test login with empty username."""
        login_data = {
            'username': '',
            'password': 'password123'
        }

        result = AuthService.login_user(login_data)

        assert result.success is False

    def test_login_user_empty_password(self):
        """Test login with empty password."""
        login_data = {
            'username': 'testuser',
            'password': ''
        }

        result = AuthService.login_user(login_data)

        assert result.success is False

    def test_login_token_is_valid_jwt(self):
        """Test that login returns a valid JWT token."""
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        result = AuthService.login_user(login_data, mock=True)

        assert result.success is True
        token = result.data['token']

        # Verify token is valid
        payload = JWTHandler.verify_token(token)
        assert payload is not None
        assert payload['username'] == 'testuser'


class TestAuthResult:
    """Tests for AuthResult dataclass."""

    def test_auth_result_success(self):
        """Test AuthResult for success case."""
        result = AuthResult(
            success=True,
            message="Operation successful",
            data={'key': 'value'}
        )

        assert result.success is True
        assert result.message == "Operation successful"
        assert result.data == {'key': 'value'}
        assert result.error is None

    def test_auth_result_failure(self):
        """Test AuthResult for failure case."""
        result = AuthResult(
            success=False,
            message="Operation failed",
            error="Invalid input"
        )

        assert result.success is False
        assert result.message == "Operation failed"
        assert result.error == "Invalid input"
        assert result.data is None


class TestIntegration:
    """Integration tests for auth flow."""

    def test_full_registration_login_flow(self):
        """Test complete registration and login flow."""
        # Register user
        user_data = {
            'username': 'integrationuser',
            'password': 'securepass123',
            'email': 'integration@test.com'
        }

        reg_result = AuthService.register_user(user_data, mock=True)
        assert reg_result.success is True

        # Login
        login_data = {
            'username': 'integrationuser',
            'password': 'securepass123'
        }

        login_result = AuthService.login_user(login_data, mock=True)
        assert login_result.success is True

        # Verify token
        token = login_result.data['token']
        payload = JWTHandler.verify_token(token)
        assert payload is not None
        assert payload['username'] == 'integrationuser'

    def test_password_hash_and_verify_integration(self):
        """Test password hashing and verification integration."""
        password = 'mySecurePassword123!'

        # Hash password
        hashed = AuthService.hash_password(password)

        # Verify correct password
        assert AuthService.verify_password(password, hashed) is True

        # Verify wrong password
        assert AuthService.verify_password('wrongPassword', hashed) is False