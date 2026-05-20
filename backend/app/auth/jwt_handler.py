# backend/app/auth/jwt_handler.py
"""
JWT Handler for token generation and verification.
"""

import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from app.config import Config


class JWTHandler:
    """Handles JWT token generation and verification."""

    ALGORITHM = 'HS256'

    @classmethod
    def generate_token(cls, user_id: str, username: str) -> str:
        """
        Generate a JWT token for a user.

        Args:
            user_id: The unique identifier for the user.
            username: The username of the user.

        Returns:
            A JWT token string.
        """
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)

        payload = {
            'user_id': user_id,
            'username': username,
            'iat': now,
            'exp': expiry
        }

        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm=cls.ALGORITHM
        )

        return token

    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token and return the payload.

        Args:
            token: The JWT token to verify.

        Returns:
            The decoded payload if valid, None if invalid or expired.
        """
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def decode_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode a JWT token without verifying expiry.

        Args:
            token: The JWT token to decode.

        Returns:
            The decoded payload if valid format, None if invalid.
        """
        try:
            # Decode without verifying expiry
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=[cls.ALGORITHM],
                options={'verify_exp': False}
            )
            return payload
        except jwt.InvalidTokenError:
            return None