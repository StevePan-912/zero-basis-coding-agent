# backend/app/config.py

import os
import secrets
import warnings
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM API配置
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')

    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        JWT_SECRET_KEY = secrets.token_urlsafe(32)
        warnings.warn('JWT_SECRET_KEY not set, using random value. Sessions will not persist across restarts.')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES') or 3600)

    # 成本控制配置
    FREE_TIER_API_LIMIT = int(os.getenv('FREE_TIER_API_LIMIT') or 50)
    PAID_TIER_API_LIMIT = int(os.getenv('PAID_TIER_API_LIMIT') or 500)

    # Flask配置
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT') or 5000)

    @classmethod
    def validate(cls):
        """Validate that all required configuration values are set."""
        required = ['DATABASE_URL', 'REDIS_URL', 'CLAUDE_API_KEY']
        missing = [k for k in required if not getattr(cls, k)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")