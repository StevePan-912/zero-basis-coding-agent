# backend/app/auth/__init__.py
"""
Authentication module.

This module provides user authentication functionality including:
- JWT token generation and verification
- Password hashing and verification
- User registration and login
"""

from app.auth.jwt_handler import JWTHandler
from app.auth.auth_service import AuthService, AuthResult

__all__ = ['JWTHandler', 'AuthService', 'AuthResult']