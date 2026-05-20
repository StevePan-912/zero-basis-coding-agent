# backend/app/database/__init__.py
"""
Database module for the application.
"""

from app.database.models import User, Conversation, TeachingContent
from app.database.teaching_content_db import TeachingContentDatabase

__all__ = [
    'User',
    'Conversation',
    'TeachingContent',
    'TeachingContentDatabase',
]