# backend/app/database/models.py
"""
Database models for the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class User:
    """
    User model for storing user information.
    """
    id: str
    username: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    difficulty_level: str = 'beginner'  # beginner, intermediate, advanced
    preferred_mode: str = 'teaching'  # teaching, practical

    def to_dict(self) -> Dict[str, Any]:
        """Convert User to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'difficulty_level': self.difficulty_level,
            'preferred_mode': self.preferred_mode
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary."""
        return cls(
            id=data['id'],
            username=data['username'],
            email=data['email'],
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            preferred_mode=data.get('preferred_mode', 'teaching')
        )


@dataclass
class Conversation:
    """
    Conversation model for storing conversation history.
    """
    id: str
    user_id: str
    session_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Conversation to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'messages': self.messages,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create Conversation from dictionary."""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            session_id=data['session_id'],
            messages=data.get('messages', []),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            updated_at=datetime.fromisoformat(data['updated_at']) if isinstance(data.get('updated_at'), str) else data.get('updated_at', datetime.now())
        )


@dataclass
class TeachingContent:
    """
    TeachingContent model for storing programming concepts and teaching materials.
    """
    id: str
    concept_name: str
    difficulty_level: str  # beginner, intermediate, advanced
    explanation: str
    analogies: List[str] = field(default_factory=list)
    code_examples: List[Dict[str, str]] = field(default_factory=list)
    visual_diagrams: List[Dict[str, str]] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert TeachingContent to dictionary."""
        return {
            'id': self.id,
            'concept_name': self.concept_name,
            'difficulty_level': self.difficulty_level,
            'explanation': self.explanation,
            'analogies': self.analogies,
            'code_examples': self.code_examples,
            'visual_diagrams': self.visual_diagrams,
            'related_concepts': self.related_concepts,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeachingContent':
        """Create TeachingContent from dictionary."""
        return cls(
            id=data['id'],
            concept_name=data['concept_name'],
            difficulty_level=data['difficulty_level'],
            explanation=data['explanation'],
            analogies=data.get('analogies', []),
            code_examples=data.get('code_examples', []),
            visual_diagrams=data.get('visual_diagrams', []),
            related_concepts=data.get('related_concepts', []),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now())
        )