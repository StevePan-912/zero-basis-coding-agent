# backend/app/auth/auth_service.py
"""
Authentication Service for user registration, login, and password management.
"""

import bcrypt
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4

from app.auth.jwt_handler import JWTHandler
from app.database.models import User


@dataclass
class AuthResult:
    """Result of an authentication operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AuthService:
    """Service for handling user authentication."""

    # Validation constants
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 20
    MIN_PASSWORD_LENGTH = 6

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: The plain text password to hash.

        Returns:
            The hashed password as a string.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: The plain text password to verify.
            hashed: The hashed password to compare against.

        Returns:
            True if the password matches, False otherwise.
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception:
            return False

    @classmethod
    def _validate_user_data(cls, user_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate user registration data.

        Args:
            user_data: Dictionary containing user data.

        Returns:
            Tuple of (is_valid, error_message).
        """
        username = user_data.get('username', '')
        password = user_data.get('password', '')
        email = user_data.get('email', '')

        # Validate username
        if not username:
            return False, "Username is required"

        if len(username) < cls.MIN_USERNAME_LENGTH:
            return False, f"Username must be at least {cls.MIN_USERNAME_LENGTH} characters"

        if len(username) > cls.MAX_USERNAME_LENGTH:
            return False, f"Username must be at most {cls.MAX_USERNAME_LENGTH} characters"

        # Validate password
        if not password:
            return False, "Password is required"

        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters"

        # Validate email
        if not email:
            return False, "Email is required"

        if '@' not in email or '.' not in email:
            return False, "Invalid email format"

        # Additional email format validation
        # Email should have proper structure: local-part@domain.tld
        parts = email.split('@')
        if len(parts) != 2:
            return False, "Invalid email format"

        local_part, domain = parts
        if not local_part or not domain:
            return False, "Invalid email format"

        # Domain should contain at least one dot and valid characters
        domain_parts = domain.split('.')
        if len(domain_parts) < 2:
            return False, "Invalid email format"

        # Check for suspicious patterns in email (potential injection)
        suspicious_patterns = ['--', ';', "'", '"', 'DROP', 'SELECT', 'INSERT', 'UPDATE', 'DELETE']
        for pattern in suspicious_patterns:
            if pattern.lower() in email.lower():
                return False, "Invalid email format"

        return True, ""

    @classmethod
    def register_user(cls, user_data: Dict[str, Any], mock: bool = False) -> AuthResult:
        """
        Register a new user.

        Args:
            user_data: Dictionary containing username, password, and email.
            mock: If True, return mock success without actual DB operations.

        Returns:
            AuthResult indicating success or failure.
        """
        # Validate input
        is_valid, error_msg = cls._validate_user_data(user_data)
        if not is_valid:
            return AuthResult(
                success=False,
                message="Validation failed",
                error=error_msg
            )

        username = user_data['username']
        password = user_data['password']
        email = user_data['email']

        # Mock mode - return success without DB operations
        if mock:
            return AuthResult(
                success=True,
                message="User registered successfully (mock mode)",
                data={
                    'user_id': str(uuid4()),
                    'username': username,
                    'email': email
                }
            )

        # Hash the password
        hashed_password = cls.hash_password(password)

        # Create user object
        user = User(
            id=str(uuid4()),
            username=username,
            email=email
        )

        # In a real implementation, you would save to database here
        # For now, return success with user data
        return AuthResult(
            success=True,
            message="User registered successfully",
            data={
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'hashed_password': hashed_password
            }
        )

    @classmethod
    def login_user(cls, login_data: Dict[str, Any], mock: bool = False) -> AuthResult:
        """
        Login a user and generate a JWT token.

        Args:
            login_data: Dictionary containing username and password.
            mock: If True, return mock success without actual DB operations.

        Returns:
            AuthResult with token on success, or error on failure.
        """
        username = login_data.get('username', '')
        password = login_data.get('password', '')

        # Basic validation
        if not username:
            return AuthResult(
                success=False,
                message="Login failed",
                error="Username is required"
            )

        if not password:
            return AuthResult(
                success=False,
                message="Login failed",
                error="Password is required"
            )

        # Mock mode - return success with mock token
        if mock:
            user_id = str(uuid4())
            token = JWTHandler.generate_token(user_id, username)
            return AuthResult(
                success=True,
                message="Login successful (mock mode)",
                data={
                    'user_id': user_id,
                    'username': username,
                    'token': token
                }
            )

        # In a real implementation, you would:
        # 1. Look up user by username in database
        # 2. Verify password against stored hash
        # 3. Generate token if valid

        # For now, return a mock success (without mock=True, this would need DB)
        user_id = str(uuid4())
        token = JWTHandler.generate_token(user_id, username)

        return AuthResult(
            success=True,
            message="Login successful",
            data={
                'user_id': user_id,
                'username': username,
                'token': token
            }
        )